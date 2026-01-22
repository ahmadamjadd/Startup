# Roomify

# Roomify - Smart Hostel Roommate Matching Platform

## About

**Roomify** is a professional startup venture led by three Junior Computer Science students, focused on improving student well-being by solving the problem of incompatible roommates. Our mission is to eliminate the academic and personal struggles caused by bad living situations through a data-driven matching platform.

### Business Model

- **Freemium Model**: Students pay **Rs. 50** to unlock contact details of their top three matches, while other matches remain free to view
- **Zero Startup Costs**: Currently using free resources with plans to migrate to AWS as we scale
- **Marketing Strategy**: University-specific campaigns and strong social media presence using relatable content on Instagram
- **Current Status**: Product is finished and we are currently in the sales phase

---

## Technical Architecture

### Backend (Django)

**Framework**: Django 5.2.8 with SQLite database

**Core Models**:
- `User` (Django's built-in authentication)
- `RoommateProfile`: Stores user preferences (sleep schedule, cleanliness level, noise tolerance, study habits, phone number)
- `MatchInteraction`: Tracks user interactions, match scores, and WhatsApp clicks for analytics

**Key Features**:
- **Email Verification**: Users must verify their email before account activation
- **Session Management**: Secure login/logout with Django's authentication system
- **Phone Number Validation**: Pakistani format (03XXXXXXXXX) with uniqueness check
- **Admin Dashboard**: Full Django admin integration with filtering and search capabilities

### Machine Learning Engine

**Algorithm**: Linear Regression (scikit-learn) with StandardScaler for feature normalization

**Training Process**:
- **Ground Truth Generation**: Uses heuristic-based scoring to generate training labels
  - Sleep schedule mismatch: -25 points
  - Study habit mismatch: -15 points
  - Cleanliness difference: -5 points per level
  - Noise tolerance difference: -5 points per level
- **Feature Engineering**: 6 features extracted from profile pairs (sleep_diff, study_diff, cleanliness_diff, noise_diff, user_cleanliness, user_noise)
- **Automatic Retraining**: Model automatically retrains whenever the profile count increases by 5 new users (e.g., after 5, 10, 15, 20 profiles). This ensures the ML model continuously improves as more data becomes available, learning from the growing user base to provide better compatibility predictions.
- **Model Persistence**: Trained model saved as `trained_recommender.joblib` using joblib
- **Fallback System**: Uses heuristic scoring when ML model is unavailable (less than 1 profile)

**Scoring Logic**:
- Starts at 100% compatibility
- Deducts points based on differences in lifestyle preferences
- Final score clamped between 0-100%

### Frontend

**Framework**: Bootstrap 5.3.0 with custom CSS

**Design System**:
- **Color Palette**: Navy (#0A2647), Blue (#2C74B3), Light Blue (#E3F2FD), White
- **Components**: Responsive cards, modern navbar, clean forms, match display cards
- **Icons**: Bootstrap Icons for visual elements

**Pages**:
- Registration with email verification
- Login (email-based authentication)
- Behavioral Quiz (profile creation)
- Dashboard (Top 5 matches with compatibility scores)
- Metrics Dashboard (admin-only analytics)

**User Experience**:
- WhatsApp integration for direct contact
- Phone number prompt for visibility
- Real-time match score display
- Responsive design for mobile and desktop

### Data Flow

1. **Registration** → User creates account → Email verification required
2. **Login** → Email/password authentication → Redirects to quiz if profile incomplete
3. **Quiz** → User fills behavioral preferences → Profile saved
4. **Dashboard** → ML model calculates compatibility → Displays top 5 matches
5. **Interaction** → User clicks WhatsApp → Tracked in `MatchInteraction` model

### Analytics & Metrics

**Admin Metrics Dashboard** tracks:
- **MCR (Match Click Rate)**: Percentage of matches that result in WhatsApp clicks
- **PCR (Profile Completion Rate)**: Percentage of users who complete their profile
- **Average Top Score**: Average compatibility score of top matches

### Dependencies

- Django 5.2.8
- scikit-learn (LinearRegression, StandardScaler)
- pandas, numpy (data processing)
- joblib (model serialization)
- python-dotenv (environment variables)
- Bootstrap 5.3.0 (CDN)

### Deployment Notes

- Currently using SQLite (development)
- Email configured via Gmail SMTP
- Model file (`trained_recommender.joblib`) stored locally
- Environment variables required: `EMAIL_ADDRESS`, `EMAIL_HOST_PASSWORD`
- Plans to migrate to AWS for production scaling

---

**Built with ❤️ by the Roomify Team**
