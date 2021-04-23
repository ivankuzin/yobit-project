import yobit

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    test = yobit.Yobit("xrp", "doge")
    test.available()
    test.last_price()
    '''
    test.depth_to(0.00000500)
    test.depth_to(0.00000600)
    test.last_trade()
    test.last_trades(5)
    test.sell_price_by_amount(1)
    test.buy_price_by_amount(0.5)'''
    print(test.get_sell_price(0.5))
