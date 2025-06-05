-- Passengers Table: Stores passenger information
CREATE TABLE Passengers (
    passenger_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Flights Table: Stores flight details
CREATE TABLE Flights (
    flight_number VARCHAR(10) PRIMARY KEY,
    departure VARCHAR(50) NOT NULL,
    destination VARCHAR(50) NOT NULL,
    departure_time TIMESTAMP NOT NULL,
    arrival_time TIMESTAMP NOT NULL,
    gate VARCHAR(10),
    status VARCHAR(20) DEFAULT 'On Time',
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    availability INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bookings Table: Links passengers to flights
CREATE TABLE Bookings (
    booking_id VARCHAR(10) PRIMARY KEY,
    passenger_id VARCHAR(10) NOT NULL,
    flight_number VARCHAR(10) NOT NULL,
    booking_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Confirmed',
    total_price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (passenger_id) REFERENCES Passengers(passenger_id),
    FOREIGN KEY (flight_number) REFERENCES Flights(flight_number)
);

-- Boarding_Passes Table: Stores boarding pass details
CREATE TABLE Boarding_Passes (
    boarding_pass_id VARCHAR(10) PRIMARY KEY,
    booking_id VARCHAR(10) NOT NULL,
    gate VARCHAR(10),
    seat VARCHAR(5),
    boarding_time TIMESTAMP,
    pdf_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id)
);

-- Trips Table: Stores trip details (e.g., flight + hotel packages)
CREATE TABLE Trips (
    trip_id VARCHAR(10) PRIMARY KEY,
    passenger_id VARCHAR(10) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'Confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (passenger_id) REFERENCES Passengers(passenger_id)
);

-- Trip_Components Table: Links trips to flights, hotels, etc.
CREATE TABLE Trip_Components (
    component_id SERIAL PRIMARY KEY,
    trip_id VARCHAR(10) NOT NULL,
    component_type VARCHAR(20) NOT NULL, -- e.g., 'Flight', 'Hotel'
    flight_number VARCHAR(10), -- NULL if not a flight
    hotel_name VARCHAR(100), -- NULL if not a hotel
    check_in_date DATE,
    check_out_date DATE,
    price DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES Trips(trip_id),
    FOREIGN KEY (flight_number) REFERENCES Flights(flight_number)
);

-- Seats Table: Tracks seat assignments
CREATE TABLE Seats (
    seat_id SERIAL PRIMARY KEY,
    booking_id VARCHAR(10) NOT NULL,
    flight_number VARCHAR(10) NOT NULL,
    seat_number VARCHAR(5) NOT NULL,
    additional_fee DECIMAL(10, 2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id),
    FOREIGN KEY (flight_number) REFERENCES Flights(flight_number)
);

-- Insurance Table: Stores insurance purchases
CREATE TABLE Insurance (
    insurance_id VARCHAR(10) PRIMARY KEY,
    booking_id VARCHAR(10), -- NULL if trip-related
    trip_id VARCHAR(10), -- NULL if flight-related
    coverage_type VARCHAR(20) NOT NULL, -- e.g., 'Flight', 'Trip'
    coverage_amount DECIMAL(10, 2) NOT NULL,
    premium DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id),
    FOREIGN KEY (trip_id) REFERENCES Trips(trip_id)
);

-- Offers Table: Stores flight or trip offers
CREATE TABLE Offers (
    offer_id VARCHAR(10) PRIMARY KEY,
    offer_type VARCHAR(20) NOT NULL, -- e.g., 'Flight', 'Trip'
    flight_number VARCHAR(10), -- NULL if trip offer
    trip_id VARCHAR(10), -- NULL if flight offer
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    discount VARCHAR(10), -- e.g., '10%'
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (flight_number) REFERENCES Flights(flight_number),
    FOREIGN KEY (trip_id) REFERENCES Trips(trip_id)
);

-- Indexes for frequent queries
CREATE INDEX idx_bookings_passenger_id ON Bookings(passenger_id);
CREATE INDEX idx_bookings_flight_number ON Bookings(flight_number);
CREATE INDEX idx_trips_passenger_id ON Trips(passenger_id);
CREATE INDEX idx_seats_booking_id ON Seats(booking_id);
CREATE INDEX idx_insurance_booking_id ON Insurance(booking_id);
CREATE INDEX idx_offers_flight_number ON Offers(flight_number);