import React, { useEffect, useState } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { FiFilter, FiGrid, FiList } from 'react-icons/fi'
import ProductCard from '../../components/ProductCard/ProductCard'
import { fetchProducts, setFilters } from '../../store/slices/productsSlice'
import './Products.css'

const Products = () => {
  const { category } = useParams()
  const [searchParams] = useSearchParams()
  const dispatch = useDispatch()
  const { items: products, loading, filters } = useSelector((state) => state.products)
  const [viewMode, setViewMode] = useState('grid')
  const [showFilters, setShowFilters] = useState(false)
  const [selectedCategories, setSelectedCategories] = useState([])
  const [selectedPriceRanges, setSelectedPriceRanges] = useState([])
  const [selectedRatings, setSelectedRatings] = useState([])
  const [selectedBrands, setSelectedBrands] = useState([])
  const [currentPage, setCurrentPage] = useState(1)
  const [filteredProducts, setFilteredProducts] = useState([])
  const itemsPerPage = 12

  useEffect(() => {
    const search = searchParams.get('search')
    dispatch(setFilters({ category, search }))
    dispatch(fetchProducts({ category, search }))
  }, [category, searchParams, dispatch])

  // Apply filters whenever products or filter selections change
  useEffect(() => {
    let result = [...products]

    // Filter by categories
    if (selectedCategories.length > 0 && !selectedCategories.includes('All Products')) {
      result = result.filter(p => selectedCategories.includes(p.category))
    }

    // Filter by price range
    if (selectedPriceRanges.length > 0) {
      result = result.filter(p => {
        return selectedPriceRanges.some(range => {
          return p.price >= range.min && p.price <= range.max
        })
      })
    }

    // Filter by rating
    if (selectedRatings.length > 0) {
      const minRating = Math.min(...selectedRatings)
      result = result.filter(p => p.rating >= minRating)
    }

    // Filter by brand
    if (selectedBrands.length > 0) {
      result = result.filter(p => selectedBrands.some(brand => 
        p.name.toLowerCase().includes(brand.toLowerCase())
      ))
    }

    setFilteredProducts(result)
    setCurrentPage(1)
  }, [products, selectedCategories, selectedPriceRanges, selectedRatings, selectedBrands])

  const handleSortChange = (sort) => {
    dispatch(setFilters({ sort }))
    dispatch(fetchProducts({ ...filters, sort }))
  }

  const handleCategoryChange = (cat) => {
    const newCategories = selectedCategories.includes(cat)
      ? selectedCategories.filter(c => c !== cat)
      : [...selectedCategories, cat]
    setSelectedCategories(newCategories)
  }

  const handlePriceChange = (range) => {
    const newRanges = selectedPriceRanges.some(r => r.label === range.label)
      ? selectedPriceRanges.filter(r => r.label !== range.label)
      : [...selectedPriceRanges, range]
    setSelectedPriceRanges(newRanges)
  }

  const handleRatingChange = (rating) => {
    const newRatings = selectedRatings.includes(rating)
      ? selectedRatings.filter(r => r !== rating)
      : [...selectedRatings, rating]
    setSelectedRatings(newRatings)
  }

  const handleBrandChange = (brand) => {
    const newBrands = selectedBrands.includes(brand)
      ? selectedBrands.filter(b => b !== brand)
      : [...selectedBrands, brand]
    setSelectedBrands(newBrands)
  }

  const clearAllFilters = () => {
    setSelectedCategories([])
    setSelectedPriceRanges([])
    setSelectedRatings([])
    setSelectedBrands([])
  }

  // Pagination
  const totalPages = Math.ceil(filteredProducts.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentProducts = filteredProducts.slice(startIndex, endIndex)

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  const categories = [
    'All Products',
    'Electronics',
    'Gaming',
    'Accessories',
    'Smart Home',
    'Audio',
    'Cameras'
  ]

  const priceRanges = [
    { label: 'Under $50', min: 0, max: 50 },
    { label: '$50 - $200', min: 50, max: 200 },
    { label: '$200 - $500', min: 200, max: 500 },
    { label: '$500 - $1000', min: 500, max: 1000 },
    { label: 'Over $1000', min: 1000, max: 10000 },
  ]

  return (
    <div className="products-page">
      <div className="container">
        {/* Page Header */}
        <div className="page-header">
          <h1>{category ? category.charAt(0).toUpperCase() + category.slice(1) : 'All Products'}</h1>
          <p>Discover amazing deals on premium electronics</p>
        </div>

        {/* Toolbar */}
        <div className="products-toolbar">
          <button 
            className="filter-toggle"
            onClick={() => setShowFilters(!showFilters)}
          >
            <FiFilter /> Filters
          </button>

          <div className="toolbar-right">
            <select 
              className="sort-select"
              onChange={(e) => handleSortChange(e.target.value)}
              value={filters.sort}
            >
              <option value="popular">Most Popular</option>
              <option value="price-low">Price: Low to High</option>
              <option value="price-high">Price: High to Low</option>
              <option value="rating">Highest Rated</option>
              <option value="newest">Newest First</option>
            </select>

            <div className="view-toggle">
              <button 
                className={viewMode === 'grid' ? 'active' : ''}
                onClick={() => setViewMode('grid')}
              >
                <FiGrid />
              </button>
              <button 
                className={viewMode === 'list' ? 'active' : ''}
                onClick={() => setViewMode('list')}
              >
                <FiList />
              </button>
            </div>

            <span className="results-count">{filteredProducts.length} Products</span>
          </div>
        </div>

        {/* Main Content */}
        <div className="products-content">
          {/* Sidebar Filters */}
          <aside className={`filters-sidebar ${showFilters ? 'show' : ''}`}>
            <div className="filter-section">
              <h3>Categories</h3>
              <ul className="filter-list">
                {categories.map((cat) => (
                  <li key={cat}>
                    <label className="filter-checkbox">
                      <input 
                        type="checkbox" 
                        checked={selectedCategories.includes(cat)}
                        onChange={() => handleCategoryChange(cat)}
                      />
                      <span>{cat}</span>
                    </label>
                  </li>
                ))}
              </ul>
            </div>

            <div className="filter-section">
              <h3>Price Range</h3>
              <ul className="filter-list">
                {priceRanges.map((range) => (
                  <li key={range.label}>
                    <label className="filter-checkbox">
                      <input 
                        type="checkbox" 
                        checked={selectedPriceRanges.some(r => r.label === range.label)}
                        onChange={() => handlePriceChange(range)}
                      />
                      <span>{range.label}</span>
                    </label>
                  </li>
                ))}
              </ul>
            </div>

            <div className="filter-section">
              <h3>Rating</h3>
              <ul className="filter-list">
                {[4, 3, 2, 1].map((rating) => (
                  <li key={rating}>
                    <label className="filter-checkbox">
                      <input 
                        type="checkbox" 
                        checked={selectedRatings.includes(rating)}
                        onChange={() => handleRatingChange(rating)}
                      />
                      <span>⭐ {rating}+ Stars</span>
                    </label>
                  </li>
                ))}
              </ul>
            </div>

            <div className="filter-section">
              <h3>Brand</h3>
              <ul className="filter-list">
                {['Apple', 'Samsung', 'Sony', 'LG', 'Microsoft', 'Nintendo'].map((brand) => (
                  <li key={brand}>
                    <label className="filter-checkbox">
                      <input 
                        type="checkbox" 
                        checked={selectedBrands.includes(brand)}
                        onChange={() => handleBrandChange(brand)}
                      />
                      <span>{brand}</span>
                    </label>
                  </li>
                ))}
              </ul>
            </div>

            <button className="btn-clear-filters" onClick={clearAllFilters}>Clear All Filters</button>
          </aside>

          {/* Products Grid */}
          <div className="products-main">
            {loading ? (
              <div className="loading-state">
                <div className="spinner"></div>
                <p>Loading products...</p>
              </div>
            ) : filteredProducts.length === 0 ? (
              <div className="empty-state">
                <h2>No products found</h2>
                <p>Try adjusting your filters or search query</p>
              </div>
            ) : (
              <div className={`products-grid view-${viewMode}`}>
                {currentProducts.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            )}

            {/* Pagination */}
            {filteredProducts.length > 0 && totalPages > 1 && (
              <div className="pagination">
                <button 
                  className="page-btn" 
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  Previous
                </button>
                {[...Array(totalPages)].map((_, index) => (
                  <button 
                    key={index + 1}
                    className={`page-btn ${currentPage === index + 1 ? 'active' : ''}`}
                    onClick={() => handlePageChange(index + 1)}
                  >
                    {index + 1}
                  </button>
                ))}
                <button 
                  className="page-btn" 
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  Next
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Products
