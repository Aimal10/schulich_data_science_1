function predict() {
    // Collect input data
    const productType = document.getElementById('productType').value;
    const price = document.getElementById('price').value;
    const availability = document.getElementById('availability').value;

    // Create data object to send to Flask
    const inputData = {
        productType: productType,
        price: price,
        availability: availability
    };

    // Send a POST request to the Flask server
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(inputData),
    })
    .then(response => response.json())
    .then(data => {
        // Display prediction results
        document.getElementById('leadTimeResult').textContent = `Estimated Lead Time: ${data.lead_time} Days`;
        document.getElementById('costResult').textContent = `Estimated Cost: $${data.cost}`;
        document.getElementById('predictionResults').classList.remove('hidden');
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
