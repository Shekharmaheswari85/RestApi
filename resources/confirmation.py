from libs.mailgun import MailGunException
from types import new_class
from flask.helpers import make_response
from flask_restful import Resource
from flask import render_template
from models.confirmation import ConfirmationModel
from models.user import UserModel
import time
from schemas.confirmation import ConfirmationSchema
from resources.user import USER_NOT_FOUND

NOT_FOUND = "Confirmation reference Not Found"
EXPIRED = "The link has expired"
ALREADY_CONFIRMED = "Registration has already been confirmed"
RESEND_FAIL = "Internal Server Error,  failed to resend confirmation email"
RESEND_SUCCESSFUL = "E-mail confirmation successfully Re-sent."

confirmation_schema = ConfirmationSchema()


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        """Return confirmation HTML page"""
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": NOT_FOUND}, 404
        if confirmation.expired:
            return {"message": EXPIRED}, 400
        if confirmation.confirmed:
            return {"message": ALREADY_CONFIRMED}, 400
        confirmation.confirmed = True
        confirmation.save_to_db()
        header = {"Content-Type": "text/html"}
        return make_response(
            render_template("confirmation_path.html", email=confirmation.user.email),
            200,
            header,
        )


class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        """Returns confirmations for a given user. Use for testing"""
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        return {
            {
                "current_time": int(time()),
                "confirmation": [
                    confirmation_schema.dump(each)
                    for each in user.confirmation.order_by(ConfirmationModel.expire_at)
                ],
            },
            200,
        }

    @classmethod
    def post(cls, user_id: int):
        """resend confirmation email"""
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": ALREADY_CONFIRMED}, 400
                confirmation.force_to_expire()
            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": RESEND_SUCCESSFULL}, 201
        except MailGunException as e:
            return {"message": str(e)}, 500
        except:
            traceback.print_exec()
            return {"message": RESEND_FAIL}, 500
