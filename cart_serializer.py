import json

def cart_to_dict(cart: str):
    cart_list = cart.split(";")
    del cart_list[-1]
    cart = {}
    for cart_item in cart_list:
        item_as_dict = json.loads(cart_item)
        item_as_dict['quantity'] = int(item_as_dict['quantity'])
        if item_as_dict['product_id'] in cart:
            cart[item_as_dict['product_id']]['quantity'] += item_as_dict['quantity']
        else:
            cart[item_as_dict['product_id']] = item_as_dict
    print(cart)
    return cart
