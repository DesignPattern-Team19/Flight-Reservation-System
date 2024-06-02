from korean_airlines import korean_air
import Card
import pandas as pd

# 편도편 조회
flight_ids1, flight_infos1 = korean_air.proxy_server.search_flight_schedule_one_way("2024-07-03", "인천(ICN)", "벤쿠버(YVR)", 2)
flight_ids2, flight_infos2 = korean_air.proxy_server.search_flight_schedule_one_way("2024-07-09", "벤쿠버(YVR)", "인천(ICN)", 2) # 반환 값 : None, None (검색 조건에 일치하는 결과 없음)

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
# korean_air.proxy_server.search_flight_schedule_round_trip("2024-07-04", "2024-07-05", "인천(ICN)", "로마(FCO)") 

# 예약
flight_id1 = flight_ids1[0]
flight_id2 = flight_ids2[0]

passengers_info = [("Billy", "M", "1974-08-17"), ("watson", "M", "1960-04-19")]
card = Card.Card("농협카드", "Billy")
card.recharge(1000000)

# 편도 에약
t_or_f, booking_reference1 = korean_air.proxy_server.book_flight(flight_id1, None, 2, passengers_info, card)

print("예약 성공 여부 : ", str(t_or_f)) # 좌석수가 부족하면 실패, 카드 잔액이 부족해도 실패
print("예약 번호 : ", str(booking_reference1)) 

# 왕복 예약
t_or_f, booking_reference2 = korean_air.proxy_server.book_flight(flight_id1, flight_id2, 2, passengers_info, "하나투어")

print("예약 성공 여부 : ", str(t_or_f))
print("예약 번호 : ", str(booking_reference2))


# 예약 조회
reservation_info, passengers_info, payment_info = korean_air.proxy_server.check_reservation(booking_reference1)

print(pd.DataFrame(reservation_info))
print(pd.DataFrame(passengers_info))
print(pd.DataFrame(payment_info))


# 예약 취소
t_or_f = korean_air.proxy_server.cancel_flight(booking_reference1)

print("예약 취소 여부 : ", str(t_or_f))