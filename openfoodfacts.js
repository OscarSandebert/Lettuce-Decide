
function fetchProduct(barcode) {
    const url = `https://world.openfoodfacts.org/api/v2/product/${barcode}.json`;


    fetch(url, {
        method: "GET",
        headers: {
        Authorization: "Basic " + btoa("off:off"),
        "User-Agent": "lettuce-decide (oscar.sandebert@gmail.com)",
        },
    })
        .then((response) => response.json())
        .then((json) => console.log(json));
}

fetchProduct(7340131607376)