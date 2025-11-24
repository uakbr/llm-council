import tempfile
from importlib import reload

from backend import storage, config


def with_temp_data_dir():
    temp_dir = tempfile.TemporaryDirectory()
    original_config_dir = config.DATA_DIR
    original_storage_dir = storage.DATA_DIR
    config.DATA_DIR = temp_dir.name
    storage.DATA_DIR = temp_dir.name
    return temp_dir, original_config_dir, original_storage_dir


def restore_data_dir(temp_dir, original_config_dir, original_storage_dir):
    temp_dir.cleanup()
    config.DATA_DIR = original_config_dir
    storage.DATA_DIR = original_storage_dir
    reload(storage)


def test_add_assistant_message_persists_metadata():
    temp_dir, orig_config, orig_storage = with_temp_data_dir()
    try:
        conv = storage.create_conversation("test-conv")
        meta = {"label_to_model": {"Response A": "model-x"}, "aggregate_rankings": [{"model": "m", "average_rank": 1.0}]}
        storage.add_assistant_message(
            conv["id"],
            stage1=[{"model": "m1", "response": "r1"}],
            stage2=[{"model": "m1", "ranking": "FINAL RANKING:\n1. Response A"}],
            stage3={"model": "chair", "response": "final"},
            metadata=meta,
        )

        saved = storage.get_conversation(conv["id"])
        assert saved["messages"][0]["metadata"] == meta
    finally:
        restore_data_dir(temp_dir, orig_config, orig_storage)


def test_list_conversations_skips_invalid_json():
    temp_dir, orig_config, orig_storage = with_temp_data_dir()
    try:
        # Valid conversation
        conv = storage.create_conversation("valid")
        storage.add_user_message(conv["id"], "hi")
        # Invalid file
        bad_file = storage.get_conversation_path("broken")
        with open(bad_file, "w") as f:
            f.write("this is not json")

        conversations = storage.list_conversations()
        ids = [c["id"] for c in conversations]

        assert "valid" in ids
        assert "broken" not in ids
    finally:
        restore_data_dir(temp_dir, orig_config, orig_storage)


def test_add_user_message_raises_for_missing_conversation():
    temp_dir, orig_config, orig_storage = with_temp_data_dir()
    try:
        try:
            storage.add_user_message("missing", "hi")
            assert False, "Expected ValueError"
        except ValueError:
            pass
    finally:
        restore_data_dir(temp_dir, orig_config, orig_storage)


def test_update_title_and_assistant_require_existing_conversation():
    temp_dir, orig_config, orig_storage = with_temp_data_dir()
    try:
        storage.create_conversation("c1")
        storage.update_conversation_title("c1", "Title")

        try:
            storage.add_assistant_message("nope", [], [], {}, {})
            assert False, "Expected ValueError"
        except ValueError:
            pass

        try:
            storage.update_conversation_title("missing", "X")
            assert False, "Expected ValueError"
        except ValueError:
            pass
    finally:
        restore_data_dir(temp_dir, orig_config, orig_storage)
