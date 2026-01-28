import React from 'react'
import { Link } from 'react-router-dom'
import { useDispatch } from 'react-redux'
import { FiShoppingCart, FiHeart, FiStar } from 'react-icons/fi'
import { addToCart } from '../../store/slices/cartSlice'
import { toast } from 'react-toastify'
import './ProductCard.css'

const ProductCard = ({ product }) => {
  const dispatch = useDispatch()

  const handleAddToCart = (e) => {
    e.preventDefault()
    dispatch(addToCart(product))
    toast.success(`${product.name} added to cart!`)
  }

  return (
    <div className="product-card">
      <Link to={`/product/${product.id}`} className="product-image-container">
        <img src={product.image || '/placeholder.jpg'} alt={product.name} className="product-image" />
        {product.discount && (
          <span className="discount-badge">-{product.discount}%</span>
        )}
        <button className="wishlist-btn">
          <FiHeart />
        </button>
      </Link>

      <div className="product-info">
        <Link to={`/product/${product.id}`}>
          <h3 className="product-name">{product.name}</h3>
        </Link>
        
        <div className="product-rating">
          <div className="stars">
            {[...Array(5)].map((_, i) => (
              <FiStar 
                key={i} 
                className={i < Math.floor(product.rating || 4) ? 'star-filled' : 'star-empty'} 
              />
            ))}
          </div>
          <span className="rating-count">({product.reviews || 0})</span>
        </div>

        <p className="product-description">{product.description?.substring(0, 80)}...</p>

        <div className="product-footer">
          <div className="price-container">
            {product.discount ? (
              <>
                <span className="price-original">${product.price}</span>
                <span className="price-current">
                  ${(product.price * (1 - product.discount / 100)).toFixed(2)}
                </span>
              </>
            ) : (
              <span className="price-current">${product.price}</span>
            )}
          </div>

          <button className="btn-add-cart" onClick={handleAddToCart}>
            <FiShoppingCart />
            Add to Cart
          </button>
        </div>
      </div>
    </div>
  )
}

export default ProductCard
