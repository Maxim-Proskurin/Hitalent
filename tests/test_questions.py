import pytest


@pytest.mark.asyncio
async def test_create_question_success(client):
    payload = {"text": "Привет тест"}
    r = await client.post("/questions/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["id"] > 0
    assert data["text"] == payload["text"]
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_question_validation(client):
    # Пустой текст (ожидаем 422 и наше сообщение валидации)
    payload = {"text": "   "}
    r = await client.post("/questions/", json=payload)
    assert r.status_code == 422
    # детальная проверка - сообщение валидации на русском вы уже добавляли


@pytest.mark.asyncio
async def test_list_questions_pagination_sort(client):
    # подготовим несколько записей
    for i in range(5):
        await client.post("/questions/", json={"text": f"Q{i}"})
    r = await client.get(
        "/questions/", params={"limit": 3, "offset": 1, "sort_by": "id", "order": "asc"}
    )
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3
    assert items == sorted(items, key=lambda x: x["id"])


@pytest.mark.asyncio
async def test_get_question_and_delete(client):
    # создаём
    created = (await client.post("/questions/", json={"text": "К удалению"})).json()
    qid = created["id"]

    # получаем
    r_get = await client.get(f"/questions/{qid}")
    assert r_get.status_code == 200
    assert r_get.json()["id"] == qid

    # удаляем
    r_del = await client.delete(f"/questions/{qid}")
    assert r_del.status_code == 204

    # проверяем 404
    r_404 = await client.get(f"/questions/{qid}")
    assert r_404.status_code == 404
