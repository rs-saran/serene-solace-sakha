from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
import time
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue


class MemoryManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MemoryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path="data/qdrant", collection_name="sakha_activity_memories", embedding_size=384):
        if hasattr(self, "_initialized") and self._initialized:
            return  # Prevent reinitialization

        self.client = QdrantClient(path=db_path)
        self.collection_name = collection_name
        self.embedding_size = embedding_size
        self.embedder = None

        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.embedding_size, distance=Distance.COSINE)
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="user_id",
                field_schema="uuid",
            )

        self._initialized = True  # Mark instance as initialized

    def embed_text(self, text):
        from fastembed import TextEmbedding
        self.embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        return self.embedder.embed(text)

    def store_memory(self, user_id, thread_id, activity_id, user_situation,
                     activity_name, duration, is_completed, enjoyment_score, reason_for_skipping, feedback_updated_at):

        text_to_embed = f"User situation: {user_situation}"
        embedding = list(self.embed_text(text_to_embed))[0]

        point = PointStruct(
            id=int(time.time() * 1000),

            payload={
                "user_id": user_id,
                "thread_id": thread_id,
                "activity_id": activity_id,
                "user_situation": user_situation,
                "activity_name": activity_name,
                "duration": duration,
                "is_completed": is_completed,
                "enjoyment_score": enjoyment_score,
                "reason_for_skipping": reason_for_skipping,
                "timestamp": feedback_updated_at
            },
            vector=embedding
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

    def summarize_memory_payload_to_points(self, payload: dict) -> str:
        if payload is None:
            print("No memory payload provided.")
            return None

        user_situation = payload.get("user_situation", "an unspecified situation")
        activity_name = payload.get("activity_name", "an activity")
        duration = payload.get("duration", "some time")
        is_completed = payload.get("is_completed", False)
        enjoyment_score = payload.get("enjoyment_score", None)
        reason_for_skipping = payload.get("reason_for_skipping", "")

        summary = f"- Situation: {user_situation}\n"
        summary += f"  Activity Suggested: {activity_name} ({duration} minutes)\n"

        if is_completed:
            summary += f"  Outcome: Completed\n"
            summary += f"  Enjoyment: {enjoyment_score}/5\n"
        else:
            summary += f"  Outcome: Skipped\n"
            if reason_for_skipping:
                summary += f"  Reason: {reason_for_skipping}\n"

        return summary

    def process_results(self, raw_results):
        fetched_points = raw_results.model_dump()['points']
        print(fetched_points)
        results = None
        if len(fetched_points) > 0:
            results = [self.summarize_memory_payload_to_points(point.get("payload", None)) for point in fetched_points]
        if results is None:
            print("no memory points fetched")
            return None

        return "-----\n".join(results)

    def retrieve_activity_memories(self, query_user_situation, user_id, top_k=3):
        query_text = f"User situation: {query_user_situation}"
        query_embedding = list(self.embed_text(query_text))[0]

        raw_results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=top_k,
            query_filter=Filter(
                must=[
                    FieldCondition(key="user_id", match=MatchValue(value=user_id))
                ]
            )

        )

        print(raw_results)
        print("\n\n\n")

        results = self.process_results(raw_results)

        return results

    def close(self):
        self.client.close()