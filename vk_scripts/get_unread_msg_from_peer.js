// var peer_id = 123;
var convs = API.messages.getConversationsById({"peer_ids": peer_id, "extended": 1}); 
var count_unread = convs.items[0].unread_count;
var history = API.messages.getHistory({"peer_id": peer_id, "count": count_unread, "extended": 1, "rev": 0, "fields": "id,first_name,last_name,online_info"}); // Максимум 200 сообщений
var result = {"peer_id": peer_id, "messages": history.items, "profiles": history.profiles};
return result;
