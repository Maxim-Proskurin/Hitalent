import pytest


@pytest.mark.asyncio
async def test_create_answer_flow(client):
    # cначала создаём вопрос
    q = (await client.post("/questions/", json={"text": "Вопрос для ответа"})).json()
    qid = q["id"]

    # создаём ответ
    payload = {"user_id": "00000000-0000-0000-0000-000000000000", "text": "Мой ответ"}
    r_ans = await client.post(f"/questions/{qid}/answers/", json=payload)
    assert r_ans.status_code == 201
    ans = r_ans.json()
    assert ans["id"] > 0
    assert ans["question_id"] == qid
    assert ans["text"] == payload["text"]

    # получаем ответ
    r_get = await client.get(f"/answers/{ans['id']}")
    assert r_get.status_code == 200
    assert r_get.json()["id"] == ans["id"]

    # удаляем ответ
    r_del = await client.delete(f"/answers/{ans['id']}")
    assert r_del.status_code == 204

    # 404 после удаления
    r_404 = await client.get(f"/answers/{ans['id']}")
    assert r_404.status_code == 404


@pytest.mark.asyncio
async def test_answer_validation_text_required(client):
    q = (await client.post("/questions/", json={"text": "Вопрос"})).json()
    qid = q["id"]

    # пустой текст
    payload = {"user_id": "00000000-0000-0000-0000-000000000000", "text": "   "}
    r = await client.post(f"/questions/{qid}/answers/", json=payload)
    assert r.status_code == 422
