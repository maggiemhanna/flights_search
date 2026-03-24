import { useState } from 'react';
import ChatWidget from './ChatWidget';

function App() {
  const [searchParams, setSearchParams] = useState({
    origin: 'Paris',
    destination: 'New York',
    departure_date: '2026-05-10',
    return_date: '2026-05-20',
    passengers: 1,
    direct: false,
    max_price: '',
    max_stops: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [flights, setFlights] = useState([]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSearchParams((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : (name === 'passengers' ? parseInt(value, 10) : value),
    }));
  };

  const fetchFlights = async (params) => {
    setLoading(true);
    setError(null);
    setFlights([]);

    const payload = {
      origin: params.origin,
      destination: params.destination,
      departure_date: params.departure_date,
      return_date: params.return_date,
      passengers: params.passengers,
      filters: {
        ...(params.direct && { direct: true }),
        ...(params.max_price && { max_price: parseInt(params.max_price, 10) }),
        ...(params.max_stops !== '' && { max_stops: parseInt(params.max_stops, 10) }),
      }
    };

    try {
      const response = await fetch('http://127.0.0.1:8006/run-flights-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.status === 'success' && data.results && data.results[0]?.flights) {
        setFlights(data.results[0].flights);
      } else {
        setError('No flights found or invalid response format.');
      }
    } catch (err) {
      setError(`Failed to fetch flights: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    await fetchFlights(searchParams);
  };

  return (
    <div className="container">
      <header>
        <h1>✈️ Flights Search Simulator</h1>
        <p>Powered by Google ADK & FastAPI</p>
      </header>

      <div className="glass-panel search-bar">
        <form onSubmit={handleSearch}>
          <div className="form-group">
            <label>Origin</label>
            <input type="text" name="origin" value={searchParams.origin} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Destination</label>
            <input type="text" name="destination" value={searchParams.destination} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Departure Date</label>
            <input type="date" name="departure_date" value={searchParams.departure_date} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Return Date</label>
            <input type="date" name="return_date" value={searchParams.return_date} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Passengers</label>
            <input type="number" name="passengers" value={searchParams.passengers} onChange={handleChange} min="1" required />
          </div>

          <div className="form-group-checkbox">
            <label className="checkbox-label">
              <input type="checkbox" name="direct" checked={searchParams.direct} onChange={handleChange} />
              Direct Only
            </label>
          </div>

          <div className="form-group">
            <label>Max Price (USD)</label>
            <input type="number" name="max_price" value={searchParams.max_price} onChange={handleChange} placeholder="e.g. 1000" />
          </div>

          <div className="form-group">
            <label>Max Stops</label>
            <input type="number" name="max_stops" value={searchParams.max_stops} onChange={handleChange} placeholder="e.g. 1" min="0" />
          </div>

          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Searching...' : 'Search Flights'}
          </button>
        </form>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="results-container">
        {loading && <div className="loader">Analyzing flight paths...</div>}

        {!loading && flights.length > 0 && (
          <div className="flights-grid">
            {flights.map((flight, idx) => (
              <div key={idx} className="flight-card glass-panel">
                <div className="flight-card-header">
                  <h3>{flight.airline}</h3>
                  <span className="price">{flight.price}</span>
                </div>
                <div className="flight-card-body">
                  <p><strong>Flight:</strong> {flight.flight_number}</p>
                  <p><strong>Route:</strong> {flight.origin} ➔ {flight.destination}</p>
                  <p><strong>Times:</strong> {flight.departure_time} - {flight.arrival_time}</p>
                  <p><strong>Stops:</strong> {flight.stops} {flight.stopover_cities.length > 0 && `(${flight.stopover_cities.join(', ')})`}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && flights.length === 0 && !error && (
          <div className="empty-state">No flights loaded yet. Try searching!</div>
        )}
      </div>
      <ChatWidget flights={flights} setFlights={setFlights} searchParams={searchParams} setSearchParams={setSearchParams} fetchFlights={fetchFlights} />
    </div>
  );
}

export default App;
