from asiana_airlines import asiana_air
import pandas as pd
import Card

# 편도편 조회
flight_ids1, flight_infos1 = asiana_air.proxy_server.check_flight_schedule_one_way("2024-07-01", "인천(ICN)", "토론토(YYZ)")
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
card = Card.Card("농협카드", "Billy")
card.recharge(1000000)

# 편도 에약 - 카드를 통한
t_or_f, booking_reference1 = asiana_air.proxy_server.book_flight(flight_id1, None, 2, passengers_info, card)

print("예약 성공 여부 : ", str(t_or_f)) # 항공편 좌석이 부족해 실패
print("예약 번호 : ", str(booking_reference1))

# 편도 예약 - 여행사를 통한
t_or_f, booking_reference2 = asiana_air.proxy_server.book_flight(flight_id2, None, 2, passengers_info, "와이페이모어")

print("예약 성공 여부 : ", str(t_or_f)) # 성공
print("예약 번호 : ", str(booking_reference2))

# 예약 조회
reservation_info, passengers_info, payment_info = asiana_air.proxy_server.check_reservation(booking_reference2) # 해당 예약번호는 없거나 올바르지 않아, None, None, None을 반환

print(pd.DataFrame(reservation_info))
print(pd.DataFrame(passengers_info))
print(pd.DataFrame(payment_info))

# 예약 취소
t_or_f = asiana_air.proxy_server.cancel_flight(booking_reference1)

print("예약 취소 여부 : ", str(t_or_f))