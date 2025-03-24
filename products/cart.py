class Cart:
    def __init__(self,request):
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {"name": product.name, "price": str(product.price), "quantity": quantity}
        else:
            self.cart[product_id]["quantity"] += quantity
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def get_items(self):
        items = []
        for product_id, item in self.cart.items():
            item["id"] = product_id
            items.append(item)
        return items

    def clear(self):
        self.session["cart"] = {}
        self.session.modified = True