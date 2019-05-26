from dangapp.models import *
class CartItem():
    def __init__(self,book,amount):
        self.book=book
        self.amount=amount
        self.status=1

class Cart():
    def __init__(self):
        self.save_price=0
        self.total_price=0
        self.cartItem=[]

    #计算购物车中的金额
    def sums(self):
        self.total_price=0
        self.save_price=0
        for i in self.cartItem:
            self.total_price+=i.book.book_dprice*i.amount
            self.save_price+=(i.book.book_price-i.book.book_dprice)*i.amount

    #像购物车中添加书籍
    def add_book_toCart(self,bookId,num):
        for i in self.cartItem:
            if i.book.book_id==int(bookId):
                i.amount+=num
                self.sums()
                return
        book=TBook.objects.get(book_id=int(bookId))
        self.cartItem.append(CartItem(book,num))
        self.sums()
    #修改购物车的商品信息
    def modify_cart(self,bookId,amount):
        for i in self.cartItem:
            if i.book.book_id==bookId:
                i.amount=amount
        self.sums()
    #删除购物车
    def delete_book(self,bookId):
        for i in self.cartItem:
            if i.book.book_id==bookId:
                self.cartItem.remove(i)
        self.sums()



