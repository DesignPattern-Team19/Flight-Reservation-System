from asiana_airlines import asiana_air
from jeju_airlines import jeju_air
from korean_airlines import korean_air
import Card
from enum import Enum
from datetime import time


def check_all_flight_schedule_one_way(departure_date, departing_from, arriving_at, passengers_count):
    all_flight_schedule = list()

    flight_ids1, flight_infos1 = asiana_air.proxy_server.check_flight_schedule_one_way(departure_date, departing_from, arriving_at, passengers_count)
    flight_ids2, flight_infos2 = jeju_air.proxy_server.query_flight_schedule_one_way(departure_date, departing_from, arriving_at, passengers_count)
    flight_ids3, flight_infos3 = korean_air.proxy_server.search_flight_schedule_one_way(departure_date, departing_from, arriving_at, passengers_count)

    if (flight_infos1 != None):
        for i in range(len(flight_infos1)):
            flight_infos1[i]["Flight id"] = flight_ids1[i]
            all_flight_schedule.append(flight_infos1[i])

    if (flight_infos2 != None):
        for i in range(len(flight_infos2)):
            flight_infos2[i]["Flight id"] = flight_ids2[i]
            all_flight_schedule.append(flight_infos2[i])

    if (flight_infos3 != None):
        for i in range(len(flight_infos3)):
            flight_infos3[i]["Flight id"] = flight_ids3[i]
            all_flight_schedule.append(flight_infos3[i])

    return all_flight_schedule

def check_all_flight_schedule_round_trip(departure_date, return_date, departing_from, arriving_at, passengers_count):
    out_bound_flights = check_all_flight_schedule_one_way(departure_date, departing_from, arriving_at, passengers_count)
    in_bound_flights = check_all_flight_schedule_one_way(return_date, arriving_at, departing_from, passengers_count)

    flight_combination_list = list()

    for i in range(len(out_bound_flights)):
        for j in range(len(in_bound_flights)):
            if (out_bound_flights[i]["Date"] == in_bound_flights[j]["Date"]):
                if (out_bound_flights[i]["Arrival time"] >= in_bound_flights["Departure time"]):
                    continue

            flight_combination_list.append((i, j))

    return out_bound_flights, in_bound_flights, flight_combination_list

class PassengersInfoAndPayment:
    def __init__(self, out_bound_airline_name, out_bound_flight_id, in_bound_airline_name, in_bound_flight_id, passengers_count, price):
        self.out_bound_airline_name = out_bound_airline_name
        self.out_bound_flight_id = out_bound_flight_id
        self.in_bound_airline_name = in_bound_airline_name
        self.in_bound_flight_id = in_bound_flight_id
        self.price = price
        self.passengers_count = passengers_count
        self.passengers_info = None
        self.card = None

    def setPassengers(self, passengers_info):
        self.passengers_info = passengers_info

    def setPaymentMethod(self, card : Card):
        self.card = card

    def pay(self):
        if (self.passengers_info == None or self.card == None):
            return None, None, None, None
        
        # 카드 잔액 확인
        balance = self.card.get_balance()

        if (balance < self.price * self.passengers_count):
            return None, None, None, None
        
        t_or_f, out_bound_booking_reference = None, None

        if self.out_bound_airline_name == "아시아나 항공":
            t_or_f, out_bound_booking_reference = asiana_air.proxy_server.book_flight(self.out_bound_flight_id, None, self.passengers_count, self.passengers_info, self.card)
        elif self.out_bound_airline_name == "제주 항공":
            t_or_f, out_bound_booking_reference = jeju_air.proxy_server.book_flight(self.out_bound_flight_id, None, self.passengers_count, self.passengers_info, self.card)
        elif self.out_bound_airline_name == "대한 항공":
            t_or_f, out_bound_booking_reference = korean_air.proxy_server.book_flight(self.out_bound_flight_id, None, self.passengers_count, self.passengers_info, self.card)

        if (t_or_f == False):
            return None, None, None, None        
        
        if (self.in_bound_airline_name != None):
            in_bound_booking_reference = None

            if self.out_bound_airline_name == "아시아나 항공":
                t_or_f, in_bound_booking_reference = asiana_air.proxy_server.book_flight(self.in_bound_flight_id, None, self.passengers_count, self.passengers_info, self.card_name)
            elif self.out_bound_airline_name == "제주 항공":
                t_or_f, in_bound_booking_reference = jeju_air.proxy_server.book_flight(self.in_bound_flight_id, None, self.passengers_count, self.passengers_info, self.card_name)
            elif self.out_bound_airline_name == "대한 항공":
                t_or_f, in_bound_booking_reference = korean_air.proxy_server.book_flight(self.in_bound_flight_id, None, self.passengers_count, self.passengers_info, self.card_name)

            if (t_or_f == False):
                return self.out_bound_airline_name, out_bound_booking_reference, None, None # 일어나서는 안되는 일
            else:
                return self.in_bound_airline_name, out_bound_booking_reference, self.in_bound_airline_name, in_bound_booking_reference
            
        return self.out_bound_airline_name, out_bound_booking_reference, None, None

class SORTING_TYPE(Enum):
    DEPARTURE_TIME = 1
    PRICE = 2
    FLIGHT_TIME = 3

class Flight_one_item:
    def __init__(self, passengers_count, out_bound_flight_info, in_bound_flight_info = None):
        self.passengers_count = passengers_count

        self.out_bound_airline_name = out_bound_flight_info["Airline name"]
        self.out_bound_flight_id = out_bound_flight_info["Flight id"]
        self.out_bound_flight_info = out_bound_flight_info
        self.price = out_bound_flight_info["Price(KRW)"]

        if(in_bound_flight_info != None):
            self.in_bound_airline_name = in_bound_flight_info["Airline name"]
            self.in_bound_flight_id = in_bound_flight_info["Flight id"]
            self.price += in_bound_flight_info["Price(KRW)"]
        self.in_bound_flight_info = in_bound_flight_info

    def get_value_for_sorting(self, sorting_type : SORTING_TYPE):
        if (sorting_type == SORTING_TYPE.FLIGHT_TIME):
            if (self.in_bound_flight_info == None):
                return self.out_bound_flight_info["Flight time"]
            else:
                # 왕복 시간은 24시간을 넘지 않는다고 가정
                minute = self.out_bound_flight_info["Flight time"].minute + self.in_bound_flight_info["Flight time"].minute

                hour = self.out_bound_flight_info["Flight time"].hour + self.in_bound_flight_info["Flight time"].hour + minute // 60
                minute = minute % 60

                if (hour >= 24): 
                    hour = 23
                    minute = 59
                    second = 59

                flight_time = time(hour = hour, minute = minute, second = second)

                return flight_time

        elif (sorting_type == SORTING_TYPE.PRICE):
            return self.price
            
        else:
            return self.out_bound_flight_info["Departure time"]


    def show(self):
        obinfo = self.out_bound_flight_info
        if (self.in_bound_flight_info == None):
            print("--------------------------------------------------------------------------------------")
            print("{0}     {1} {2} -> {3} {4}      {5}        {6}원(1인당)".format(self.out_bound_airline_name, obinfo["Departure city"], obinfo["Departure time"],  
                                                           obinfo["Arrival city"], obinfo["Arrival time"], obinfo["Flight time"], self.price))
            print("--------------------------------------------------------------------------------------")
            print("")
        else:
            ibinfo = self.in_bound_flight_info

            if (obinfo["Airline name"] == ibinfo["Airline name"]):
                print("--------------------------------------------------------------------------------------")
                print("{0}     {1} {2} -> {3} {4}      {5}".format(self.out_bound_airline_name, obinfo["Departure city"], obinfo["Departure time"],  
                                                           obinfo["Arrival city"], obinfo["Arrival time"], obinfo["Flight time"]))
                print("        {0} {1} -> {2} {3}      {4}        {5}원(1인당)".format(ibinfo["Departure city"], ibinfo["Departure time"],  
                                                           ibinfo["Arrival city"], ibinfo["Arrival time"], ibinfo["Flight time"], self.price))
                print("--------------------------------------------------------------------------------------")
                print("")
            else:
                print("--------------------------------------------------------------------------------------")
                print("{0}     {1} {2} -> {3} {4}      {5}".format(self.out_bound_airline_name, obinfo["Departure city"], obinfo["Departure time"],  
                                                           obinfo["Arrival city"], obinfo["Arrival time"], obinfo["Flight time"]))
                print("{0}     {1} {2} -> {3} {4}      {5}        {6}원(1인당)".format(self.in_bound_airline_name, ibinfo["Departure city"], ibinfo["Departure time"],  
                                                           ibinfo["Arrival city"], ibinfo["Arrival time"], ibinfo["Flight time"], self.price))
                print("--------------------------------------------------------------------------------------")
                print("")
        
        # 가장 저렴한 결제수단과 가격 출력
        
    # def click()
    # 이 개체를 클릭시 카드사별 최저가격을 개체 형식으로 출력?

    def click(self):
        if (self.in_bound_flight_info == None):
            return PassengersInfoAndPayment(self.out_bound_airline_name, self.out_bound_flight_id, None, None, self.passengers_count, self.price)
        else:
            return PassengersInfoAndPayment(self.out_bound_airline_name, self.out_bound_flight_id, self.in_bound_airline_name, self.in_bound_flight_id, self.passengers_count, self.price)


class Flight_item_list:
    def __init__(self):
        self.flight_item_list = list()

    def add_item(self, flight_item):
        self.flight_item_list.append(flight_item)

    def show(self, sorting_type : SORTING_TYPE):
        self.flight_item_list.sort(key = lambda one_item: one_item.get_value_for_sorting(sorting_type))
        
        for flight_one_item in self.flight_item_list:
            flight_one_item.show()

    def click(self, index):
        return self.flight_item_list[index]

def get_flight_item_list(departure_date, return_date, departing_from, arriving_at, passengers_count):
    flight_item_list = Flight_item_list()

    if (return_date == None):
        all_flight_schedule_one_way = check_all_flight_schedule_one_way(departure_date, departing_from, arriving_at, passengers_count)

        for flight_schedule in all_flight_schedule_one_way:
            flight_item_list.add_item(Flight_one_item(passengers_count, flight_schedule))
    else:
        out_bound_flights, in_bound_flights, combination_list = check_all_flight_schedule_round_trip(departure_date, return_date, departing_from, arriving_at, passengers_count)

        for combination in combination_list:
            flight_item_list.add_item(Flight_one_item(passengers_count, out_bound_flights[combination[0]], in_bound_flights[combination[1]]))

    return flight_item_list

# 조회 -> 개체에 담기 -> 개체를 정렬할 컨테이너 역활


flight_item_list1 = get_flight_item_list("2024-07-04", None, "인천(ICN)", "로마(FCO)", 2)
flight_item_list1.show(SORTING_TYPE.PRICE)

flight_item_list2 = get_flight_item_list("2024-07-04", "2024-07-09", "인천(ICN)", "로마(FCO)", 2)
flight_item_list2.show(SORTING_TYPE.FLIGHT_TIME)

flight_one_item = flight_item_list1.click(0)
payment = flight_one_item.click()

passengers_info = [("Billy", "M", "1974-08-17"), ("watson", "M", "1960-04-19")]
card = Card.Card("농협카드", "Billy")
card.recharge(1000000)

payment.setPassengers(passengers_info)
payment.setPaymentMethod(card)
print(payment.pay()) # 반드시 승객수를 맞출것, 위 2와 passengers_info의 원소의 개수를 일치시켜야


