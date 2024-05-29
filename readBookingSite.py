"""
해결할 것
--------------------------------------------------------------------------------------

- 엑셀 시트에서 값을 못가지고 옴.

--------------------------------------------------------------------------------------
"""

import pandas as pd

class FlightInfo:
    def __init__(self, date, airline, departure, departure_time, arrival, arrival_time, duration, NH_price, KB_price, WOORI_price):
        self.date = date
        self.airline = airline
        self.departure = departure
        self.departure_time = departure_time
        self.arrival = arrival
        self.arrival_time = arrival_time
        self.duration = duration
        self.card_prices = {
            '농협': NH_price,
            '국민': KB_price,
            '우리': WOORI_price,
        }

def load_flights(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    flights = []
    for index, row in df.iterrows():
        flight = FlightInfo(
            row['Date'], row['Airline'], row['Departure'], row['Departure Time'],
            row['Arrival'], row['Arrival Time'], row['Duration'], row['NH Price'],
            row['KB Price'], row['WOORI Price']
        )
        flights.append(flight)
    return flights

class Command:
    def execute(self):
        pass

class SearchFlightCommand(Command):
    def __init__(self, flights1, flights2, depart_date, return_date, departure, arrival):
        self.flights1 = flights1
        self.flights2 = flights2
        self.depart_date = depart_date
        self.return_date = return_date
        self.departure = departure
        self.arrival = arrival
    
    def execute(self):
        depart_results1 = [f for f in self.flights1 if f.date == self.depart_date and f.departure == self.departure and f.arrival == self.arrival]
        depart_results2 = [f for f in self.flights2 if f.date == self.depart_date and f.departure == self.departure and f.arrival == self.arrival]
        return_results1 = [f for f in self.flights1 if f.date == self.return_date and f.departure == self.arrival and f.arrival == self.departure]
        return_results2 = [f for f in self.flights2 if f.date == self.return_date and f.departure == self.arrival and f.arrival == self.departure]
        return (depart_results1, depart_results2), (return_results1, return_results2)

class SelectFlightCommand(Command):
    def __init__(self, depart_flight, return_flight):
        self.depart_flight = depart_flight
        self.return_flight = return_flight
    
    def execute(self):
        return {
            '출발': self.depart_flight.card_prices,
            '귀환': self.return_flight.card_prices
        }

class PaymentCommand(Command):
    def __init__(self, card_type):
        self.card_type = card_type
    
    def execute(self):
        # 결제 로직을 구현.
        return f"결제 완료: {self.card_type} 카드 사용"

class PaymentStrategy:
    def pay(self, amount):
        pass

class Card1PaymentStrategy(PaymentStrategy):
    def pay(self, amount):
        return f"Card1로 {amount}원 결제 완료"

class Card2PaymentStrategy(PaymentStrategy):
    def pay(self, amount):
        return f"Card2로 {amount}원 결제 완료"

class Card3PaymentStrategy(PaymentStrategy):
    def pay(self, amount):
        return f"Card3로 {amount}원 결제 완료"

def main():
    file_path = r"C:\Users\DELL\Downloads\설계패턴 19조.xlsx"  # 파일 경로를 raw string으로 지정
    sheet_name1 = '와이페이모어'  # 와이페이모어 시트 이름
    sheet_name2 = '하나투어'  # 하나투어 시트 이름

    flights1 = load_flights(file_path, sheet_name1)
    flights2 = load_flights(file_path, sheet_name2)
    
    # 사용자가 입력한 값
    depart_date = '7-1'
    return_date = '7-7'
    departure = '인천(ICN)'
    arrival = '토론토(YYZ)'
    
    # 엑셀 시트에서 검색
    depart_results1 = [f for f in flights1 if f.date == depart_date and f.departure == departure and f.arrival == arrival]
    print(depart_results1)
    depart_results2 = [f for f in flights2 if f.date == depart_date and f.departure == departure and f.arrival == arrival]
    return_results1 = [f for f in flights1 if f.date == return_date and f.departure == arrival and f.arrival == departure]
    return_results2 = [f for f in flights2 if f.date == return_date and f.departure == arrival and f.arrival == departure]
    
    # 결과 출력
    print("와이페이모어 출발 항공편:")
    for flight in depart_results1:
        print(f"항공사: {flight.airline}, 출발: {flight.departure_time}, 도착: {flight.arrival_time}, 카드사별 가격: {flight.card_prices}")
    
    print("\n하나투어 출발 항공편:")
    for flight in depart_results2:
        print(f"항공사: {flight.airline}, 출발: {flight.departure_time}, 도착: {flight.arrival_time}, 카드사별 가격: {flight.card_prices}")
    
    print("\n와이페이모어 귀환 항공편:")
    for flight in return_results1:
        print(f"항공사: {flight.airline}, 출발: {flight.departure_time}, 도착: {flight.arrival_time}, 카드사별 가격: {flight.card_prices}")
    
    print("\n하나투어 귀환 항공편:")
    for flight in return_results2:
        print(f"항공사: {flight.airline}, 출발: {flight.departure_time}, 도착: {flight.arrival_time}, 카드사별 가격: {flight.card_prices}")
    
    # 예시: 사용자가 와이페이모어에서 첫 번째 출발 및 귀환 항공편 선택
    if depart_results1 and return_results1:
        selected_depart_flight = depart_results1[0]
        selected_return_flight = return_results1[0]
        select_flight_command = SelectFlightCommand(selected_depart_flight, selected_return_flight)

if __name__ == "__main__":
    main()
