            if grep -q 'Content-Type: application/javascript' "$0"; then
                echo "Znaleziono plik JavaScript, wyodrębniam..."
                mkdir -p extracted_content/js
                # Extract JavaScript content between boundaries
                sed -n '/Content-Type: application\/javascript/,/--WEBAPP_BOUNDARY_/p' "$0" | \

EOM
            # Add JavaScript content from the extracted file
            if [ -f "extracted_content/js/app.js" ]; then
                cat extracted_content/js/app.js >> "$TMP_EML"
            fi
            
            # Add favicon if exists
            if [ -f "extracted_content/images/favicon.svg" ]; then
                cat >> "$TMP_EML" <<- EOM


EOM
                base64 < extracted_content/images/favicon.svg >> "$TMP_EML"
            fi
            
            # Close boundaries
            echo -e "\n--RELATED_BOUNDARY_12345--" >> "$TMP_EML"
            echo -e "\n--WEBAPP_BOUNDARY_12345--" >> "$TMP_EML"

function showAll() {
    const cards = document.querySelectorAll('.invoice-card');
    cards.forEach(card => card.style.display = 'flex');
}

function filterByStatus(status) {
    const cards = document.querySelectorAll('.invoice-card');
    cards.forEach(card => {
        if (card.dataset.status === status) {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
}

// Animacja ładowania
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.invoice-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';

        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    console.log('Dashboard faktur załadowany - Maj 2025');
});

