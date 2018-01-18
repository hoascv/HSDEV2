from flask import jsonify,g,request
#from hswebapp import db
from hswebapp.api import apiv0
from hswebapp.api.auth import basic_auth,token_auth


@apiv0.route('/tokens', methods=['GET'])
@basic_auth.login_required
def get_token():
    
    token = g.current_user.get_token()
    id = g.current_user.id
    expire = g.current_user.token_expiration
    
    
    return jsonify({"status":200,"id":id, 
    "access":{"access_token":token,"expires_in":expire,"token_type":"Bearer" }})
    
    
    

@apiv0.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    g.current_user.revoke_token()
    return jsonify({'user':g.current_user.username}), 204

