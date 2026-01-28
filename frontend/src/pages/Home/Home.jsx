import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FiTruck, FiShield, FiCreditCard, FiHeadphones, FiArrowRight } from 'react-icons/fi'
import ProductCard from '../../components/ProductCard/ProductCard'
import { productsAPI } from '../../services/api'
import './Home.css'

const Home = () => {
  const [featuredProducts, setFeaturedProducts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadFeaturedProducts()
  }, [])

  const loadFeaturedProducts = async () => {
    try {
      const response = await productsAPI.getAll({ limit: 8, featured: true })
      setFeaturedProducts(response.data.products || response.data)
    } catch (error) {
      console.error('Error loading products:', error)
    } finally {
      setLoading(false)
    }
  }

  const categories = [
    { name: 'Electronics', slug: 'electronics', icon: '💻', color: '#6366f1' },
    { name: 'Gaming', slug: 'gaming', icon: '🎮', color: '#8b5cf6' },
    { name: 'Accessories', slug: 'accessories', icon: '🎧', color: '#ec4899' },
    { name: 'Smart Home', slug: 'smart-home', icon: '🏠', color: '#10b981' },
  ]

  const features = [
    { icon: <FiTruck />, title: 'Free Shipping', desc: 'On orders over $50' },
    { icon: <FiShield />, title: '2 Year Warranty', desc: 'On all products' },
    { icon: <FiCreditCard />, title: 'Secure Payment', desc: '100% secure checkout' },
    { icon: <FiHeadphones />, title: '24/7 Support', desc: 'Dedicated support team' },
  ]

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="container hero-container">
          <div className="hero-content">
            <h1 className="hero-title">
              Premium Electronics
              <span className="gradient-text"> At Your Fingertips</span>
            </h1>
            <p className="hero-description">
              Discover the latest gadgets, gaming gear, and electronics. 
              Shop with confidence and get the best deals on premium products.
            </p>
            <div className="hero-buttons">
              <Link to="/products" className="btn-hero-primary">
                Shop Now <FiArrowRight />
              </Link>
              <Link to="/products/gaming" className="btn-hero-secondary">
                Gaming Gear
              </Link>
            </div>
          </div>
          <div className="hero-image">
            <div className="hero-gradient-orb"></div>
            <img src="https://images.unsplash.com/photo-1468495244123-6c6c332eeece?w=600" alt="Electronics" />
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="categories-section">
        <div className="container">
          <h2 className="section-title">Shop by Category</h2>
          <div className="categories-grid">
            {categories.map((category) => (
              <Link 
                key={category.slug}
                to={`/products/${category.slug}`}
                className="category-card"
                style={{ '--category-color': category.color }}
              >
                <span className="category-icon">{category.icon}</span>
                <h3>{category.name}</h3>
                <FiArrowRight className="category-arrow" />
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="products-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Featured Products</h2>
            <Link to="/products" className="view-all">
              View All <FiArrowRight />
            </Link>
          </div>
          
          {loading ? (
            <div className="loading">Loading products...</div>
          ) : (
            <div className="products-grid">
              {featuredProducts.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Features */}
      <section className="features-section">
        <div className="container">
          <div className="features-grid">
            {features.map((feature, index) => (
              <div key={index} className="feature-card">
                <div className="feature-icon">{feature.icon}</div>
                <div>
                  <h3>{feature.title}</h3>
                  <p>{feature.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Newsletter */}
      <section className="newsletter-section">
        <div className="container">
          <div className="newsletter-content">
            <h2>Subscribe to Our Newsletter</h2>
            <p>Get the latest updates on new products and exclusive offers</p>
            <form className="newsletter-form">
              <input type="email" placeholder="Enter your email" required />
              <button type="submit">Subscribe</button>
            </form>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Home
