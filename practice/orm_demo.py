from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models import Base, Training, User

def main():
    engine = create_engine("sqlite:///:memory:", echo=True)

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        original_autocommit = dbapi_connection.autocommit
        dbapi_connection.autocommit = True

        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()
            dbapi_connection.autocommit = original_autocommit

    Base.metadata.create_all(engine)

    with engine.connect() as connection:
        enabled = connection.exec_driver_sql(
            "PRAGMA foreign_keys"
        ).scalar()
        print("外键检查是否开启：", enabled)

    # 下面保留原来的两个 Session 代码块


    with Session(engine) as session:
        user = User(username="Richard")
        session.add(user)
        session.flush()

        print("用户 ID：", user.id)
        record = Training(
            user=user,
            date="2026-10-23",
            shots=10,
            made=7
        )
        

        session.add(record)
        session.commit()

        record_id = record.id
        print("保存后的 ID：", record_id)

    with Session(engine) as query_session:
        saved_record = query_session.get(Training, record_id)
        print("训练所属用户：", saved_record.user.username)
        saved_user = saved_record.user
        print("该用户的训练条数：", len(saved_user.trainings))

        print(
            "新会话查询结果：",
            saved_record.id,
            saved_record.date,
            saved_record.shots,
            saved_record.made
        )
        statement = select(Training).where(
            Training.date == "2026-10-23"
        )

        records = query_session.scalars(statement).all()

        print("该日期的训练条数：", len(records))

    with Session(engine) as test_session:
        invalid_record = Training(
             user_id=999,
             date="2026-10-24",
             shots=10,
            made=7
        )
        test_session.add(invalid_record)

        try:
            test_session.commit()
        except IntegrityError as error:
            test_session.rollback()
            print("数据库拒绝了无效记录：", error.orig)

            remaining_records = test_session.scalars(
                select(Training)
            ).all()

            assert len(remaining_records) == 1, "回滚后应该只剩一条正常记录"
            assert remaining_records[0].user_id == 1, "正常记录应属于用户 1"

            print("回滚后训练记录总数：", len(remaining_records))
            print(
                "剩余记录的用户 ID：",
                [record.user_id for record in remaining_records]
            )
        else:
            raise AssertionError(
                "外键检查失效：不存在的用户竟然保存成功"
            )


            print("回滚后训练记录总数：", len(remaining_records))
            print(
                "剩余记录的用户 ID：",
                [record.user_id for record in remaining_records]
            )  

if __name__ == "__main__":
    main()