// Form validation
document.addEventListener('DOMContentLoaded', function() {
    // Aadhaar number validation
    const aadhaarInput = document.getElementById('aadhaar');
    if (aadhaarInput) {
        aadhaarInput.addEventListener('input', function(e) {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    }
    
    // Mobile number validation
    const mobileInput = document.getElementById('mobile');
    if (mobileInput) {
        mobileInput.addEventListener('input', function(e) {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    }
    
    // OTP validation
    const otpInput = document.getElementById('otp');
    if (otpInput) {
        otpInput.addEventListener('input', function(e) {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    }
    
    // Form submission with loading state
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                submitButton.disabled = true;
            }
        });
    });
    
    // Candidate selection animation
    const candidateCards = document.querySelectorAll('.candidate-card');
    candidateCards.forEach(card => {
        const radio = card.querySelector('input[type="radio"]');
        const label = card.querySelector('.candidate-label');
        
        label.addEventListener('click', function() {
            // Remove selected class from all cards
            candidateCards.forEach(c => {
                c.querySelector('.candidate-label').classList.remove('selected');
            });
            
            // Add selected class to current card
            this.classList.add('selected');
        });
    });
    
    // Live results update (for demo purposes)
    const resultsPage = document.querySelector('.results-container');
    if (resultsPage) {
        // In a real app, this would fetch from the API
        console.log('Results page loaded');
    }
});
