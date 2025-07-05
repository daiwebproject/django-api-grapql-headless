import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
# from graphene_subscriptions.constants import GRAPHQL_WS_PROTOCOL
from api.schema import schema

class GraphQLConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.subprotocol = 'graphql-ws'  # or 'graphql-transport-ws' based on your implementation
        await self.accept(subprotocol=self.subprotocol)
    
    async def disconnect(self, close_code):
        pass
    
    async def receive(self, text_data):
        try:
            message = json.loads(text_data)
            
            if message['type'] == 'start':
                query = message['payload']['query']
                variables = message.get('payload', {}).get('variables', {})
                
                # Execute subscription
                result = await self.execute_subscription(query, variables)
                
                await self.send(text_data=json.dumps({
                    'type': 'data',
                    'id': message['id'],
                    'payload': result
                }))
        
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'payload': {'message': str(e)}
            }))
    
    @database_sync_to_async
    def execute_subscription(self, query, variables):
        result = schema.execute(query, variables=variables)
        return {
            'data': result.data,
            'errors': [str(error) for error in result.errors] if result.errors else None
        }