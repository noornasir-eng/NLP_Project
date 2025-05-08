import grpc
from concurrent import futures
import time
import agent_pb2_grpc
import agent_pb2
from finalnlpbackend import process_input, translate_story, get_trending_topics  # Updated import

# Implement the service defined in the proto
class AgentService(agent_pb2_grpc.AgentServicer):

    def GenerateStory(self, request, context):
        try:
            # Your custom backend logic
            result = process_input(
                topic=request.topic,
                genre=request.genre,
                length=request.length,
                tone=request.tone,
                characters=request.characters
            )
            return agent_pb2.StoryResponse(story=result)
        except Exception as e:
            context.set_details(f'Error: {str(e)}')
            context.set_code(grpc.StatusCode.INTERNAL)
            return agent_pb2.StoryResponse(story="Error generating story")

    def TranslateStory(self, request, context):
        try:
            translated = translate_story(request.story, request.language)
            return agent_pb2.TranslateResponse(translated_story=translated)
        except Exception as e:
            context.set_details(f'Error: {str(e)}')
            context.set_code(grpc.StatusCode.INTERNAL)
            return agent_pb2.TranslateResponse(translated_story="Error translating story")
            
    def GetTrendingTopics(self, request, context):
        try:
            topics = get_trending_topics()
            return agent_pb2.TopicsResponse(topics=topics)
        except Exception as e:
            context.set_details(f'Error: {str(e)}')
            context.set_code(grpc.StatusCode.INTERNAL)
            return agent_pb2.TopicsResponse(topics=[])

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    agent_pb2_grpc.add_AgentServicer_to_server(AgentService(), server)
    server.add_insecure_port('[::]:50051')
    print("gRPC server running on port 50051...")
    server.start()
    try:
        while True:
            time.sleep(86400)  # Run forever
    except KeyboardInterrupt:
        print("Stopping server...")
        server.stop(0)

if __name__ == '__main__':
    serve()
