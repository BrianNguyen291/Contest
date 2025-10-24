import React, { useState, useEffect } from 'react'
import { Search, Plane, Clock, DollarSign, Award, Loader2, AlertCircle, CheckCircle } from 'lucide-react'
import axios from 'axios'
import { format } from 'date-fns'

const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [searchForm, setSearchForm] = useState({
    origin: 'LAX',
    destination: 'JFK',
    date: format(new Date(), 'yyyy-MM-dd'),
    passengers: 1
  })
  
  const [searchResults, setSearchResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [airports, setAirports] = useState([])

  // Load airports on component mount
  useEffect(() => {
    loadAirports()
  }, [])

  const loadAirports = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/airports`)
      setAirports(response.data.airports)
    } catch (err) {
      console.error('Failed to load airports:', err)
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setSearchForm(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSearchResults(null)

    try {
      const response = await axios.post(`${API_BASE_URL}/api/search`, searchForm)
      
      if (response.data.success) {
        setSearchResults(response.data.data)
      } else {
        setError(response.data.error || 'Search failed')
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Network error')
    } finally {
      setLoading(false)
    }
  }

  const swapAirports = () => {
    setSearchForm(prev => ({
      ...prev,
      origin: prev.destination,
      destination: prev.origin
    }))
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container py-6">
          <div className="flex items-center justify-center space-x-3">
            <Plane className="h-8 w-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">AA Flight Scraper</h1>
          </div>
          <p className="text-center text-gray-600 mt-2">
            Search American Airlines flights with award and cash pricing comparison
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container py-8">
        {/* Search Form */}
        <div className="card mb-8">
          <div className="card-header">
            <h2 className="text-2xl font-bold text-gray-900 flex items-center">
              <Search className="h-6 w-6 mr-2" />
              Search Flights
            </h2>
          </div>
          
          <form onSubmit={handleSearch} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Origin Airport */}
              <div className="form-group">
                <label className="form-label">From</label>
                <select
                  name="origin"
                  value={searchForm.origin}
                  onChange={handleInputChange}
                  className="form-select"
                  required
                >
                  {airports.map(airport => (
                    <option key={airport.code} value={airport.code}>
                      {airport.code} - {airport.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Destination Airport */}
              <div className="form-group">
                <label className="form-label">To</label>
                <select
                  name="destination"
                  value={searchForm.destination}
                  onChange={handleInputChange}
                  className="form-select"
                  required
                >
                  {airports.map(airport => (
                    <option key={airport.code} value={airport.code}>
                      {airport.code} - {airport.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Date */}
              <div className="form-group">
                <label className="form-label">Departure Date</label>
                <input
                  type="date"
                  name="date"
                  value={searchForm.date}
                  onChange={handleInputChange}
                  className="form-input"
                  required
                />
              </div>

              {/* Passengers */}
              <div className="form-group">
                <label className="form-label">Passengers</label>
                <select
                  name="passengers"
                  value={searchForm.passengers}
                  onChange={handleInputChange}
                  className="form-select"
                >
                  {[1, 2, 3, 4, 5, 6, 7, 8].map(num => (
                    <option key={num} value={num}>{num} {num === 1 ? 'Passenger' : 'Passengers'}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                type="button"
                onClick={swapAirports}
                className="btn btn-secondary"
                disabled={loading}
              >
                <Plane className="h-4 w-4" />
                Swap Airports
              </button>
              
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="h-4 w-4" />
                    Search Flights
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="alert alert-error fade-in">
            <AlertCircle className="h-5 w-5 inline mr-2" />
            {error}
          </div>
        )}

        {/* Search Results */}
        {searchResults && (
          <div className="fade-in">
            {/* Search Summary */}
            <div className="card mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">
                    {searchResults.search_metadata.origin} → {searchResults.search_metadata.destination}
                  </h3>
                  <p className="text-gray-600">
                    {format(new Date(searchResults.search_metadata.date), 'EEEE, MMMM do, yyyy')} • 
                    {searchResults.search_metadata.passengers} {searchResults.search_metadata.passengers === 1 ? 'Passenger' : 'Passengers'}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-green-600">
                    {searchResults.total_results} Flights Found
                  </div>
                  <div className="text-sm text-gray-600">
                    {searchResults.flights.filter(f => f.cpp !== null).length} with CPP data
                  </div>
                </div>
              </div>
            </div>

            {/* Flight Results */}
            {searchResults.flights.length > 0 ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {searchResults.flights.map((flight, index) => (
                  <FlightCard key={index} flight={flight} />
                ))}
              </div>
            ) : (
              <div className="card text-center">
                <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No Flights Found</h3>
                <p className="text-gray-600">Try adjusting your search criteria</p>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-50 mt-12">
        <div className="container py-8">
          <div className="text-center text-gray-600">
            <p>AA Flight Scraper - Compare award and cash pricing</p>
            <p className="text-sm mt-2">Powered by advanced web scraping technology</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function FlightCard({ flight }) {
  return (
    <div className="flight-card fade-in">
      <div className="flight-header">
        <div className="flight-number">{flight.flight_number}</div>
        <div className="flex items-center space-x-2">
          {flight.cpp !== null ? (
            <div className="flex items-center text-green-600">
              <CheckCircle className="h-4 w-4 mr-1" />
              <span className="text-sm font-medium">CPP Available</span>
            </div>
          ) : (
            <div className="flex items-center text-gray-500">
              <AlertCircle className="h-4 w-4 mr-1" />
              <span className="text-sm">Limited Data</span>
            </div>
          )}
        </div>
      </div>

      <div className="flight-times">
        <div className="time-group">
          <div className="time-label">Departure</div>
          <div className="time-value">{flight.departure_time}</div>
        </div>
        <div className="time-group">
          <div className="time-label">Arrival</div>
          <div className="time-value">{flight.arrival_time}</div>
        </div>
      </div>

      <div className="flight-pricing">
        {flight.cash_price_usd && (
          <div className="price-item">
            <div className="price-label">Cash Price</div>
            <div className="price-value">
              <DollarSign className="h-4 w-4 inline mr-1" />
              {flight.cash_price_usd.toFixed(2)}
            </div>
          </div>
        )}

        {flight.points_required && (
          <div className="price-item">
            <div className="price-label">Award Points</div>
            <div className="price-value">
              <Award className="h-4 w-4 inline mr-1" />
              {flight.points_required.toLocaleString()}
            </div>
          </div>
        )}

        {flight.cpp && (
          <div className="price-item col-span-2">
            <div className="cpp-label">Cents Per Point</div>
            <div className="cpp-value">{flight.cpp.toFixed(2)}¢</div>
          </div>
        )}
      </div>

      {flight.taxes_fees_usd && (
        <div className="mt-4 text-sm text-gray-600">
          <Clock className="h-4 w-4 inline mr-1" />
          Taxes & Fees: ${flight.taxes_fees_usd.toFixed(2)}
        </div>
      )}
    </div>
  )
}

export default App
