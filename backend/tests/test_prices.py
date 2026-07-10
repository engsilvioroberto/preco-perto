import pytest

@pytest.mark.asyncio
async def test_price_comparison_no_product(client):
    response = await client.get(
        "/api/v1/prices/product/nonexistent",
        params={"lat": -21.1767, "lng": -47.8208, "radius": 10}
    )
    assert response.status_code == 404
