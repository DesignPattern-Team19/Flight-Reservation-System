from asiana_airlines import asiana_air
import pandas as pd

# 편도편 조회
flight_ids1, flight_infos1 = asiana_air.proxy_server.check_flight_schedule_one_way("2024-07-04", "인천(ICN)", "로마(FCO)")
flight_ids2, flight_infos2 = asiana_air.proxy_server.check_flight_schedule_one_way("2024-07-09", "로마(FCO)", "인천(ICN)")

info_count = len(flight_ids1)
for i in range(info_count):
    print("flight id : " + str(flight_ids1[i]))

    df = pd.DataFrame([flight_infos1[i]])
    print(df)

info_count = len(flight_ids2)
for i in range(info_count):
    print("flight id : " + str(flight_ids2[i]))

    df = pd.DataFrame([flight_infos2[i]])
    print(df)

# 왕복편 조회 <- 사용 금지, 아직 구현하지 않음
# proxy_server.check_flight_schedule_round_trip("2024-07-04", "2024-07-05", "인천(ICN)", "로마(FCO)") 

# 예약
flight_id1 = flight_ids1[0]
flight_id2 = flight_ids2[2]
passengers_info = [("Billy", "M", "1974-08-17"), ("watson", "M", "1960-04-19")]

# 편도 에약
t_or_f, booking_reference1 = asiana_air.proxy_server.book_flight(flight_id1, None, 2, passengers_info, "goodtrip")

print("예약 성공 여부 : ", str(t_or_f))
print("예약 번호 : ", str(booking_reference1))

# 왕복 예약
t_or_f, booking_reference2 = asiana_air.proxy_server.book_flight(flight_id1, flight_id2, 2, passengers_info, "goodtrip")

print("예약 성공 여부 : ", str(t_or_f))
print("예약 번호 : ", str(booking_reference2))

# 예약 취소
t_or_f = asiana_air.proxy_server.cancel_flight(booking_reference1)

print("예약 취소 여부 : ", str(t_or_f))