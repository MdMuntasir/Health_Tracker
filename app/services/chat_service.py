import uuid
from datetime import datetime, timezone
from app.services.db_service import delete_item, get_item, put_item, query_items
from app.services.ai_service import chat_with_summary

DEFAULT_CONVERSATION_ID = "default"
MAX_HISTORY_MESSAGES = 100
MAX_MESSAGE_CHARS = 20000
MAX_SUMMARY_CHARS = 6000


def _utc_now():
    return datetime.now(timezone.utc)


def _summary_sk(conversation_id):
    return f"AI_CHAT#{conversation_id}#SUMMARY"


def _message_prefix(conversation_id):
    return f"AI_CHAT#{conversation_id}#MSG#"


def _put_message(user_id, conversation_id, role, content):
    created_at = _utc_now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    sk = f"{_message_prefix(conversation_id)}{created_at}#{uuid.uuid4()}"
    item = {
        "user_id": user_id,
        "sk": sk,
        "conversation_id": conversation_id,
        "role": role,
        "content": content[:MAX_MESSAGE_CHARS],
        "created_at": created_at,
    }
    put_item(item)
    return item


def get_summary(user_id, conversation_id=DEFAULT_CONVERSATION_ID):
    item = get_item(
        user_id, _summary_sk(conversation_id), consistent_read=True
    ) or {}
    try:
        message_count = int(item.get("message_count", 0))
    except (TypeError, ValueError):
        message_count = 0

    return {
        "conversation_id": conversation_id,
        "summary": item.get("summary", ""),
        "message_count": message_count,
        "updated_at": item.get("updated_at"),
    }


def get_history(user_id, conversation_id=DEFAULT_CONVERSATION_ID, limit=MAX_HISTORY_MESSAGES):
    items = query_items(user_id, _message_prefix(conversation_id))
    items.sort(key=lambda item: item.get("sk", ""))
    if limit and len(items) > limit:
        items = items[-limit:]

    return [
        {
            "role": item.get("role"),
            "content": item.get("content"),
            "created_at": item.get("created_at"),
        }
        for item in items
    ]


def handle_chat(user_id, message, conversation_id=DEFAULT_CONVERSATION_ID):
    """Answer a message, persist it, and refresh the rolling conversation summary."""
    current = get_summary(user_id, conversation_id)
    previous_summary = current["summary"]

    reply, summary = chat_with_summary(message, previous_summary)

    _put_message(user_id, conversation_id, "user", message)
    _put_message(user_id, conversation_id, "assistant", reply)

    summary = summary.strip()[-MAX_SUMMARY_CHARS:]
    message_count = current["message_count"] + 2
    updated_at = _utc_now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    put_item(
        {
            "user_id": user_id,
            "sk": _summary_sk(conversation_id),
            "conversation_id": conversation_id,
            "summary": summary,
            "message_count": message_count,
            "updated_at": updated_at,
        }
    )

    return {
        "conversation_id": conversation_id,
        "reply": reply,
        "summary": summary,
        "message_count": message_count,
        "updated_at": updated_at,
    }


def get_conversation(user_id, conversation_id=DEFAULT_CONVERSATION_ID, limit=MAX_HISTORY_MESSAGES):
    summary = get_summary(user_id, conversation_id)
    return {
        "conversation_id": conversation_id,
        "summary": summary["summary"],
        "message_count": summary["message_count"],
        "updated_at": summary["updated_at"],
        "messages": get_history(user_id, conversation_id, limit),
    }


def clear_conversation(user_id, conversation_id=DEFAULT_CONVERSATION_ID):
    for item in query_items(user_id, _message_prefix(conversation_id)):
        delete_item(user_id, item["sk"])
    delete_item(user_id, _summary_sk(conversation_id))
    return {"deleted": True, "conversation_id": conversation_id}
