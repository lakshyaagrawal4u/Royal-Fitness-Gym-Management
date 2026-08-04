from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class SuperAdmin(db.Model):

    __tablename__ = "super_admin"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

class Gym(db.Model):

    __tablename__ = "gyms"

    id = db.Column(db.Integer, primary_key=True)

    gym_name = db.Column(db.String(100), nullable=False)

    owner_name = db.Column(db.String(100), nullable=False)

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(15),
        nullable=False
    )

    plan = db.Column(
        db.String(20),
        default="Basic"
    )

    plan_expiry_date = db.Column(
        db.Date,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Active"
    )

    reference_by = db.Column(
        db.String(100),
        nullable=True
    )

class Member(db.Model):

    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    phone = db.Column(
        db.String(15),
        nullable=False
    )

    age = db.Column(db.Integer)

    gender = db.Column(db.String(20))

    address = db.Column(db.String(200))

    gym_id = db.Column(
        db.Integer,
        db.ForeignKey("gyms.id"),
        nullable=False
    )

    joining_date = db.Column(db.Date, nullable=False)

    membership_plan = db.Column(db.String(50), nullable=False)

    trainer = db.Column(db.String(100))

    monthly_fee = db.Column(db.Float, nullable=False)

    status = db.Column(db.String(20), default="Active")

    # Fee paid till this date
    fee_paid_till = db.Column(
        db.Date,
        nullable=True
    )
    gym = db.relationship(
        "Gym",
        backref="members"
    )


class Payment(db.Model):

    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    gym_id = db.Column(
        db.Integer,
        db.ForeignKey("gyms.id"),
        nullable=False
    )

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
    member = db.relationship(
        "Member",
        backref="payments"
    )

    gym = db.relationship(
        "Gym",
        backref="payments"
    )

    remarks = db.Column(db.String(200))