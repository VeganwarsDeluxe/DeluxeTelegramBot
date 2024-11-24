import numpy as np
import tensorflow as tf
from VegansDeluxe import rebuild
from VegansDeluxe.core import Session, Engine, Entity, Action
from tensorflow.keras import layers, models
from tensorflow.keras.layers import Embedding


class PlayerInputModel:
    shape_size = 5

    @classmethod
    def compile_entity(cls, entity):
        return [
            entity.hp,
            entity.energy,
            entity.hit_chance,
            int(entity.weapon.ranged),
            len(entity.nearby_entities)
        ]


class BattleAI:
    def __init__(self, engine, max_opponents=1, max_actions=20, action_embedding_dim=16, ai_id="battle_ai_model"):
        self.engine = engine
        self.ai_id = ai_id

        self.max_opponents = max_opponents
        self.max_actions = max_actions
        self.action_embedding_dim = action_embedding_dim
        self.action_id_to_index = {}  # Mapping from action IDs to indices for embedding

        self.player_shape_size = PlayerInputModel.shape_size

        # Build the model
        self.model = self._build_model()
        self.model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    def save(self):
        self.model.save(f"{self.ai_id}.keras")

    def load(self):
        try:
            self.model = models.load_model(f"{self.ai_id}.keras")
        except:
            pass

    def _build_model(self):
        # Player input
        player_input = layers.Input(shape=(self.player_shape_size,), name="player_state")  # Example: [hp, energy, ...]
        player_features = layers.Dense(32, activation="relu")(player_input)

        # Opponent inputs
        opponents_input = layers.Input(shape=(self.max_opponents, self.player_shape_size),
                                       name="opponent_states")  # Each opponent has 10 attributes
        opponent_features = layers.TimeDistributed(layers.Dense(32, activation="relu"))(opponents_input)
        opponent_features = layers.GlobalMaxPooling1D()(opponent_features)  # Aggregate opponent states

        # Actions input
        actions_input = layers.Input(shape=(self.max_actions, self.action_embedding_dim), name="actions")
        action_features = layers.TimeDistributed(layers.Dense(32, activation="relu"))(actions_input)
        action_features = layers.GlobalMaxPooling1D()(action_features)  # Aggregate action features

        # Turn context input
        turn_input = layers.Input(shape=(1,), name="turn_context")
        turn_features = layers.Dense(8, activation="relu")(turn_input)

        # Combine all features
        combined_features = layers.Concatenate()([player_features, opponent_features, action_features, turn_features])
        combined_features = layers.Dense(64, activation="relu")(combined_features)

        # Output layer: Choose an action
        output = layers.Dense(self.max_actions, activation="softmax", name="action_probabilities")(combined_features)

        return models.Model(inputs=[player_input, opponents_input, actions_input, turn_input], outputs=output)

    def cultivate_dummy_action(self):
        session = Session(self.engine.event_manager)
        dummy_action = Action(session, 0)
        dummy_action.id = "dummy"
        return dummy_action

    def encode_actions(self, actions):
        """
        Encode a list of Action objects into numerical representations.
        """

        # Define a dummy action
        dummy_action = self.cultivate_dummy_action()

        # Pad or truncate actions to self.max_actions
        if len(actions) < self.max_actions:
            actions += [dummy_action] * (self.max_actions - len(actions))  # Add dummy actions
        else:
            actions = actions[:self.max_actions]  # Truncate extra actions

        if not self.action_id_to_index:
            # Build mapping from action IDs to indices
            all_action_ids = set(action.id for action in actions)
            self.action_id_to_index = {action_id: idx for idx, action_id in enumerate(sorted(all_action_ids))}

        # Extract features
        ids = [self.action_id_to_index[action.id] for action in actions]

        # Convert to tensors
        ids_tensor = np.array(ids)

        # Create embeddings
        action_id_embedding = Embedding(input_dim=len(self.action_id_to_index), output_dim=self.action_embedding_dim)
        id_embeddings = action_id_embedding(ids_tensor)

        # Concatenate numerical features
        action_representations = tf.concat([id_embeddings], axis=1)

        self.action_id_to_index = {}
        return action_representations

    def preprocess_data(self, data):
        """
        Convert raw game state data into tensors for training.
        """
        player_states = []
        opponent_states = []
        action_representations = []
        turn_numbers = []
        labels = []

        for example in data:
            # Encode player and opponent states
            player_states.append(example["player"])
            opponent_states.append(example["opponents"])

            # Encode actions
            encoded_actions = self.encode_actions(example["actions"])
            action_representations.append(encoded_actions)

            # Turn numbers and labels
            turn_numbers.append(example["turn"])
            labels.append(example["chosen_action"])

        return (
            np.array(player_states),
            np.array(opponent_states),
            np.array(action_representations),
            np.array(turn_numbers),
            np.array(labels),
        )

    async def train(self, training_data, batch_size=32, epochs=10):
        """
        Train the model using collected game state data.
        """
        player_data, opponent_data, actions_data, turn_data, action_labels = self.preprocess_data(training_data)

        # Train the model
        self.model.fit(
            [player_data, opponent_data, actions_data, turn_data],
            action_labels,
            batch_size=batch_size,
            epochs=epochs,
            verbose=0
        )

    def predict_action(self, player, opponents, actions, turn):
        """
        Predict the best action given the current game state.
        """
        # Encode game state
        encoded_player = np.array([player])
        encoded_opponents = np.array([opponents])
        encoded_actions = np.array([self.encode_actions(actions)])
        encoded_turn = np.array([turn])

        # Predict action probabilities
        action_probabilities = self.model.predict([encoded_player, encoded_opponents, encoded_actions, encoded_turn],
                                                  verbose=0)

        # Mask out dummy actions (assume dummy actions have ID=0)
        valid_mask = np.array([1 if action.id != "dummy" else 0 for action in actions])  # 1 for real, 0 for dummy
        action_probabilities[0] *= valid_mask  # Zero out probabilities for dummy actions

        # Choose the best action
        best_action_index = np.argmax(action_probabilities)
        return actions[best_action_index], self.form_action_chart(action_probabilities, actions)

    def form_action_chart(self, probabilities, actions):
        probabilities = probabilities[0]
        chart = {}
        i = 0
        for probability in probabilities:
            if actions[i].id != "dummy":
                chart[actions[i].id] = probability
            i += 1
        return chart

    def compile_entity(self, entity: Entity):
        return PlayerInputModel.compile_entity(entity)

    def compile_training_data(self, session: Session, entity: Entity, choice_index: int):
        actions = self.engine.action_manager.get_available_actions(session, entity)

        data = {
            "player": self.compile_entity(entity),
            "opponents": [self.compile_entity(player) for player in session.entities if player.id != entity.id],
            "actions": actions,
            "turn": session.turn,
            "chosen_action": choice_index  # Action which an AI should choose
        }

        return data


async def get_duel_setup():
    # Create the engine instance
    engine = Engine()

    # Create the game session and attach it to the engine
    session = Session(engine.event_manager)
    await engine.attach_session(session)

    # Attach players to the session
    session.attach_entity(player_a)
    session.attach_entity(player_b)

    for entity in session.entities:
        for state in rebuild.all_states:
            # Attach all default states to all players
            await entity.attach_state(state(), engine.event_manager)

    player_a.choose_skills()
    player_a.choose_items()
    player_b.choose_skills()
    player_b.choose_items()
