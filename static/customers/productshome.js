let counter = 1;

// Load products 14 at a time.
const quantity = 14;

// When DOM loads, render the first 20 posts.
document.addEventListener('DOMContentLoaded', load);

// If scrolled to bottom, load the next 20 posts.
window.onscroll = () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        load();
    }
};

function load() {

    // Set start and end post numbers, and update counter.
    const start = counter;
    const end = start + quantity - 1;
    counter = end + 1;

    // Open new request to get new posts.
    const request = new XMLHttpRequest();
    request.open('POST', '/');
    request.onload = () => {
           const res = JSON.parse(request.responseText);
            if (res.success) {
                
                const product_template = Handlebars.compile(document.querySelector('#products').innerHTML);
                const products = product_template({'products': res.products});
                document.querySelector('#allproducts').innerHTML += products;
            }
    };

    // Add start and end points to request data.
    const data = new FormData();
    data.append('start', start);
    data.append('end', end);

    // Send request.
    request.send(data);
};