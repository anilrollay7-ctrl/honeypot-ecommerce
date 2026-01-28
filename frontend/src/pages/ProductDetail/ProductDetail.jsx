import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { addToCart } from '../../store/slices/cartSlice';
import api from '../../services/api';
import './ProductDetail.css';

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { isAuthenticated } = useSelector((state) => state.auth);
  
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [selectedImage, setSelectedImage] = useState(0);

  useEffect(() => {
    fetchProduct();
  }, [id]);

  const fetchProduct = async () => {
    try {
      const response = await api.get(`/products/${id}`);
      setProduct(response.data);
    } catch (error) {
      console.error('Error fetching product:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = () => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: `/product/${id}` } });
      return;
    }

    dispatch(addToCart({ ...product, quantity }));
    alert('Product added to cart!');
  };

  const handleBuyNow = () => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: `/product/${id}` } });
      return;
    }

    dispatch(addToCart({ ...product, quantity }));
    navigate('/checkout');
  };

  if (loading) {
    return <div className="loading">Loading product details...</div>;
  }

  if (!product) {
    return <div className="error">Product not found</div>;
  }

  const discountPrice = product.discount 
    ? product.price * (1 - product.discount / 100) 
    : product.price;

  // Additional product images (using same image for demo)
  const images = [product.image, product.image, product.image];

  return (
    <div className="product-detail">
      <div className="product-detail-container">
        <div className="product-images">
          <div className="main-image">
            <img src={images[selectedImage]} alt={product.name} />
            {product.discount > 0 && (
              <div className="discount-badge">{product.discount}% OFF</div>
            )}
          </div>
          <div className="image-thumbnails">
            {images.map((img, index) => (
              <img
                key={index}
                src={img}
                alt={`${product.name} ${index + 1}`}
                className={selectedImage === index ? 'active' : ''}
                onClick={() => setSelectedImage(index)}
              />
            ))}
          </div>
        </div>

        <div className="product-info">
          <div className="breadcrumb">
            <span onClick={() => navigate('/')}>Home</span>
            <span>/</span>
            <span onClick={() => navigate('/products')}>Products</span>
            <span>/</span>
            <span>{product.category}</span>
          </div>

          <h1>{product.name}</h1>
          
          <div className="rating">
            <div className="stars">
              {'★'.repeat(Math.floor(product.rating))}
              {'☆'.repeat(5 - Math.floor(product.rating))}
            </div>
            <span className="rating-text">
              {product.rating} ({product.reviews} reviews)
            </span>
          </div>

          <div className="price-section">
            <div className="price">
              ${discountPrice.toFixed(2)}
              {product.discount > 0 && (
                <span className="original-price">${product.price}</span>
              )}
            </div>
            <div className="stock-status">
              {product.inStock ? (
                <span className="in-stock">✓ In Stock</span>
              ) : (
                <span className="out-of-stock">Out of Stock</span>
              )}
            </div>
          </div>

          <div className="description">
            <h3>Description</h3>
            <p>{product.description}</p>
            <ul>
              <li>High quality materials</li>
              <li>Premium build quality</li>
              <li>1 year warranty included</li>
              <li>Free shipping on orders over $100</li>
            </ul>
          </div>

          <div className="quantity-selector">
            <label>Quantity:</label>
            <div className="quantity-controls">
              <button 
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                disabled={quantity <= 1}
              >
                -
              </button>
              <input 
                type="number" 
                value={quantity} 
                onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                min="1"
              />
              <button onClick={() => setQuantity(quantity + 1)}>+</button>
            </div>
          </div>

          <div className="action-buttons">
            <button 
              className="add-to-cart-btn" 
              onClick={handleAddToCart}
              disabled={!product.inStock}
            >
              Add to Cart
            </button>
            <button 
              className="buy-now-btn" 
              onClick={handleBuyNow}
              disabled={!product.inStock}
            >
              Buy Now
            </button>
          </div>

          <div className="product-features">
            <div className="feature">
              <span className="icon">🚚</span>
              <div>
                <strong>Free Delivery</strong>
                <p>On orders over $100</p>
              </div>
            </div>
            <div className="feature">
              <span className="icon">🔒</span>
              <div>
                <strong>Secure Payment</strong>
                <p>100% secure transaction</p>
              </div>
            </div>
            <div className="feature">
              <span className="icon">↩️</span>
              <div>
                <strong>Easy Returns</strong>
                <p>30-day return policy</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
