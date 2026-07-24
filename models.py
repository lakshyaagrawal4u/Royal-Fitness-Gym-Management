from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class Member(db.Model):

    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    phone = db.Column(db.String(15), unique=True, nullable=False)

    age = db.Column(db.Integer)

    gender = db.Column(db.String(20))

    address = db.Column(db.String(200))

    joining_date = db.Column(db.Date, nullable=False)

    membership_plan = db.Column(db.String(50), nullable=False)

    trainer = db.Column(db.String(100))

    monthly_fee = db.Column(db.Float, nullable=False)

    status = db.Column(db.String(20), default="Active")

    # Fee paid till this date
    last_fee_paid = db.Column(db.Date, nullable=True)


class Payment(db.Model):

    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    member_id = db.Column(
        db.Integer,
        db.ForeignKey("members.id"),
        nullable=False
    )

    amount = db.Column(db.Float, nullable=False)

    payment_date = db.Column(db.Date, nullable=False)

    months_paid = db.Column(db.Integer, default=1)

    payment_mode = db.Column(
        db.String(20),
        nullable=False,
        default="Cash"
    )

    remarks = db.Column(db.String(200))