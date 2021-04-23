import requests
import json


class Yobit:
    """
        Provides access to Yobit.net
    """
    __url_base = "https://yobit.net/api/3/"

    def __init__(self, left="ltc", right="btc"):
        self._left = left
        self._right = right

    def __repr__(self):
        return f"Pair: {self.pair}"

    @property
    def pair(self):
        return self._left + "_" + self._right

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, left: str):
        self._left = left

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, right: str):
        self._right = right

    def available(self):
        """
            information about coin`s availability
        """
        url = Yobit.__url_base + "info"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error, status code: {response.status_code}")
            raise Exception()
        response = json.loads(response.text)
        if self.pair not in response["pairs"]:
            raise Exception()
        if response["pairs"][self.pair]["hidden"] == 0:
            print(f"Current pair {self.pair} exists...")
            return True
        if response["pairs"][self.pair]["hidden"] == 1:
            print(f"Current pair {self.pair} exists, but hidden...")
            return True
        return False

    def last_price(self, pair=""):
        """
            information about coin`s last price
        """
        current_pair = self.pair
        if pair != "":
            current_pair = pair
        url = Yobit.__url_base + "ticker/" + current_pair
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error, status code: {response.status_code}")
            return
        response = json.loads(response.text)
        print(f"Price: {current_pair} = {float(response[current_pair]['last']):.8f}")
        return response[current_pair]['last']

    def depth_to(self, value):
        """
            information about depth of coin to 'value' price
        """
        url = Yobit.__url_base + "depth/" + self.pair
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error, status code: {response.status_code}")
            return
        response = json.loads(response.text)
        depth = 0
        if value > response[self.pair]["asks"][0][0]:
            for order in response[self.pair]["asks"]:
                if value >= order[0]:
                    depth += order[1] * order[0]
                else:
                    break
            print(f"Orderbook: amount {round(depth, 4)} {self.right} in sell orders to {value:.8f} {self.left}")
            return depth
        else:
            for order in response[self.pair]["bids"]:
                if value <= order[0]:
                    depth += order[1] * order[0]
                else:
                    break
            print(f"Orderbook: amount {round(depth, 4)} {self.right} in buy  orders to {value:.8f} {self.left}")
            return depth

    def last_trade(self):
        """
            information about last trade
        """
        url = Yobit.__url_base + "trades/" + self.pair
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error, status code: {response.status_code}")
            return
        response = json.loads(response.text)
        print("Amount of last trade: ", response[self.pair][0]["amount"])
        return response[self.pair][0]

    def last_trades(self, count):
        """
            information about last 'count' trades
        """
        url = Yobit.__url_base + "trades/" + self.pair
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error, status code: {response.status_code}")
            return []
        response = json.loads(response.text)
        print(f"Last {count} trades:")
        for i in range(count):
            print(f"Amount of {i+1} trade:", response[self.pair][i]["amount"])
        return response[self.pair][:count]

    def buy_price_by_amount(self, value):
        """
            information about highest price u place in order to buy 'value' amount
        """
        url = Yobit.__url_base + "depth/" + self.pair
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error, status code: {response.status_code}")
            return
        response = json.loads(response.text)
        amount = 0
        i = 0
        for order in response[self.pair]["asks"]:
            if amount >= value:
                amount -= order[1] * order[0]
                i -= 2
                break
            amount += order[1] * order[0]
            i += 1
        if i >= 150:
            i = 149
        print(f"Buy price for spend {value} {self.right} will be: {response[self.pair]['asks'][i][0]:0.8f}")
        return response[self.pair]["asks"][i][0]

    def sell_price_by_amount(self, value):
        """
            information about lowest price u place in order to sell 'value' amount
        """
        url = Yobit.__url_base + "depth/" + self.pair
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error, status code: {response.status_code}")
            return
        response = json.loads(response.text)
        amount = 0
        i = 0
        for order in response[self.pair]["asks"]:
            if amount <= value:
                amount -= order[1] * order[0]
                i -= 2
                break
            amount += order[1] * order[0]
            i += 1
        if i >= 150:
            i = 149
        print(f"Sell price for receive {value} {self.right} will be: {response[self.pair]['bids'][i][0]:0.8f}")
        return response[self.pair]["bids"][i][0]

    def get_sell_price(self, amount, pair="doge_btc"):
        """
            the highest price to sell converted 'right' in 'pair'
        """
        print(f"Calculating volume {amount} equivalent in pair {pair}")
        price = self.last_price(pair)
        amount /= price
        price = self.buy_price_by_amount(amount)
        return price
        # Проверяем ордера в текущей паре, если цена отличается больше чем на 5% вниз и хоть немного
        # вверх - снимаем ордер и ставим по текущей цене
