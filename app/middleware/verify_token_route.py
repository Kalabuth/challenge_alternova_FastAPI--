from fastapi import Request
from fastapi.responses import JSONResponse
from utils.autentication import handle_authorization
from fastapi.routing import APIRoute

class VerifyTokenRoute(APIRoute):
    def get_route_handler(self):
        original_route = super().get_route_handler()
        
        async def verify_token_middleware(request:Request):
            if not request.headers.get('Authorization', ''):
                 return JSONResponse(content={"message": "Debe de enviar el token"}, status_code=401)
             
            token = request.headers.get('Authorization', '').split(" ")[1]
        
            validation_response = handle_authorization(token, output=False)
            print("llega acá", validation_response)
            if validation_response == None:
                return  await original_route(request)
            else:
                return validation_response
                
        return verify_token_middleware