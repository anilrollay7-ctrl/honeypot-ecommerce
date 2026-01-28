import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { FiTrash2, FiMinus, FiPlus, FiShoppingBag } from 'react-icons/fi'
import { removeFromCart, updateQuantity, clearCart } from '../../store/slices/cartSlice'
import { toast } from 'react-toastify'
import './Cart.css'

const Cart = () => {
  const navigate = useNavigate()
  const dispatch = useDispatch()
  const { items, total, itemCount } = useSelector((state) => state.cart)
  const { isAuthenticated } = useSelector((state) => state.auth)

  const handleUpdateQuantity = (id, newQuantity) => {
    if (newQuantity < 1) return
    if (newQuantity > 10) {
      toast.warning('Maximum quantity is 10')
      return
    }
    dispatch(updateQuantity({ id, quantity: newQuantity }))
  }

  const handleRemove = (id, name) => {
    dispatch(removeFromCart(id))
    toast.success(`${name} removed from cart`)
  }

  const handleClearCart = () => {
    if (window.confirm('Are you sure you want to clear your cart?')) {
      dispatch(clearCart())
      toast.info('Cart cleared')
    }
  }

  const handleCheckout = () => {
    if (!isAuthenticated) {
      toast.info('Please login to continue')
      navigate('/login')
    } else {
      navigate('/checkout')
    }
  }

  if (items.length === 0) {
    return (
      <div className="cart-page">
        <div className="container">
          <div className="empty-cart">
            <FiShoppingBag className="empty-icon" />
            <h2>Your cart is empty</h2>
            <p>Add some products to get started</p>
            <Link to="/products" className="btn-shop-now">
              Continue Shopping
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="cart-page">
      <div className="container">
        <div className="cart-header">
          <h1>Shopping Cart</h1>
          <button className="btn-clear" onClick={handleClearCart}>
            Clear Cart
          </button>
        </div>

        <div className="cart-content">
          <div className="cart-items">
            {items.map((item) => (
              <div key={item.id} className="cart-item">
                <img src={item.image || '/placeholder.jpg'} alt={item.name} />
                
                <div className="item-details">
                  <h3>{item.name}</h3>
                  <p className="item-description">{item.description}</p>
                  <div className="item-meta">
                    <span className="item-category">{item.category}</span>
                    {item.inStock ? (
                      <span className="stock-badge in-stock">In Stock</span>
                    ) : (
                      <span className="stock-badge out-stock">Out of Stock</span>
                    )}
                  </div>
                </div>

                <div className="item-quantity">
                  <button 
                    onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                    disabled={item.quantity <= 1}
                  >
                    <FiMinus />
                  </button>
                  <span>{item.quantity}</span>
                  <button 
                    onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                    disabled={item.quantity >= 10}
                  >
                    <FiPlus />
                  </button>
                </div>

                <div className="item-price">
                  <span className="price-single">${item.price}</span>
                  <span className="price-total">${(item.price * item.quantity).toFixed(2)}</span>
                </div>

                <button 
                  className="btn-remove"
                  onClick={() => handleRemove(item.id, item.name)}
                >
                  <FiTrash2 />
                </button>
              </div>
            ))}
          </div>

          <div className="cart-summary">
            <h2>Order Summary</h2>
            
            <div className="summary-row">
              <span>Subtotal ({itemCount} items)</span>
              <span>${total.toFixed(2)}</span>
            </div>

            <div className="summary-row">
              <span>Shipping</span>
              <span className="text-success">FREE</span>
            </div>

            <div className="summary-row">
              <span>Tax (Estimated)</span>
              <span>${(total * 0.1).toFixed(2)}</span>
            </div>

            <div className="summary-divider"></div>

            <div className="summary-total">
              <span>Total</span>
              <span>${(total * 1.1).toFixed(2)}</span>
            </div>

            <button className="btn-checkout" onClick={handleCheckout}>
              Proceed to Checkout
            </button>

            <Link to="/products" className="btn-continue">
              Continue Shopping
            </Link>

            <div className="trust-badges">
              <div className="badge-item">
                <span>🔒</span>
                <span>Secure Checkout</span>
              </div>
              <div className="badge-item">
                <span>📦</span>
                <span>Free Shipping</span>
              </div>
              <div className="badge-item">
                <span>↩️</span>
                <span>Easy Returns</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Cart
