import json


def cart_to_dict(cart: str):
    cart_list = cart.split(";")
    del cart_list[-1]
    for cart_item in cart_list:
        item_as_dict = json.loads(cart_item)
        item_as_dict['quantity'] = int(item_as_dict['quantity'])
        yield item_as_dict


def update_cart_quantity(cart: str, increment: bool) -> tuple:
    cart_dict = {}
    for item_as_dict in cart_to_dict(cart):
        if item_as_dict['product_id'] in cart_dict:
            if increment:
                cart_dict[item_as_dict['product_id']]['quantity'] += item_as_dict['quantity']
            else:
                cart_dict[item_as_dict['product_id']]['quantity'] = item_as_dict['quantity']
        else:
            cart_dict[item_as_dict['product_id']] = item_as_dict
    cart_str = "".join('''{
                "product_id": %d,
                "name": "%s",
                "price": %f,
                "quantity": %d 
            };''' % (v["product_id"], v["name"], v["price"], v["quantity"])
                        for v in cart_dict.values())

    return cart_dict, cart_str


def get_cart_dict(cart: str):
    cart_dict = {}
    for item_as_dict in cart_to_dict(cart):
        cart_dict[item_as_dict['product_id']] = item_as_dict
    return cart_dict
