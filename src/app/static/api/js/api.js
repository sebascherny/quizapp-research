const login_api = async (username, password, success, fail) => {
  const response = await fetch(
    `/api/token/`,
    {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        "username": username,
        "password": password,
      })
    }
  );
  const text = await response.text();
  if (response.status === 200) {
    console.log("success", JSON.parse(text));
    success(JSON.parse(text));
  } else {
    console.log("failed", text);
    fail(JSON.parse(text)["detail"])
  }
};

const do_token_not_valid = async () => {
  await localStorage.removeItem("userToken");
  await localStorage.removeItem("loggedInUsername");
  console.log("Token not valid");
  window.location = "/login";
};

const getLoggedInUsername = async (funcCall) => {
  const loggedInUsername = await localStorage.getItem("loggedInUsername");
  funcCall(loggedInUsername);
};

const register_api = async (username, password, success, fail) => {
  const response = await fetch(
    `/api/register/`,
    {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        "username": username,
        "password": password,
      })
    }
  );
  const text = await response.text();
  if (response.status === 200) {
    console.log("success", JSON.parse(text));
    success(JSON.parse(text));
  } else {
    console.log("failed", text);
    fail(JSON.parse(text)["detail"])
  }
};

const get_quizes_api = async (pageNo = "", success, fail) => {
  const token = await localStorage.getItem("userToken");
  if (token === null) {
    console.log("No credentials found, redirecting...");
    window.location = "/login";
    return [];
  }
  const response = await fetch(
    `/api/quizes/?page_no=${pageNo}`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'Application/JSON',
        'Authorization': `Bearer ${token}`,
      }
    }
  );
  const text = await response.text();
  if (response.status === 401) {
    do_token_not_valid();
    return [];
  }
  if (response.status === 200) {
    var responseObj = JSON.parse(text);
    console.log("success", responseObj);
    success(responseObj);
  } else {
    console.log("failed", text);
    Object.entries(JSON.parse(text)).forEach(([key, value]) => {
      fail(`${key}: ${value}`);
    });
  }
};

const post_quiz_api = async (data, success) => {
  const token = await localStorage.getItem("userToken");
  if (token === null) {
    console.log("No credentials found, redirecting...");
    window.location = "/login";
    return [];
  }
  const response = await fetch(
    `/api/quizes/`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'Application/JSON',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data)
    }
  );
  const text = await response.text();
  if (response.status === 401) {
    do_token_not_valid();
    return [];
  }
  if (response.status === 201) {
    console.log("success", JSON.parse(text));
    const quizObj = JSON.parse(text);
    success(quizObj);
    window.location = window.location.origin + "/dashboard/" + quizObj.data.id;
  } else {
    console.log("failed", text);
    Object.entries(JSON.parse(text)).forEach(([key, value]) => {
      fail(`${key}: ${value}`);
    });
  }
};

const post_question_api = async (quizId, question_data, success, fail) => {
  const token = await localStorage.getItem("userToken");
  if (token === null) {
    console.log("No credentials found, redirecting...");
    window.location = "/login";
    return [];
  }
  const response = await fetch(
    `/api/quizes/${quizId}/questions/`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'Application/JSON',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(question_data)
    }
  );
  const text = await response.text();
  if (response.status === 401) {
    do_token_not_valid();
    return [];
  }
  if (response.status === 201) {
    console.log("success", JSON.parse(text));
    success(JSON.parse(text));
  } else {
    console.log("failed", text);
    fail(JSON.parse(text));
  }
};

const delete_question_api = async (quizId, questionId, success, fail) => {
  if (questionId == null) {
    success();
    return;
  }
  const token = await localStorage.getItem("userToken");
  if (token === null) {
    console.log("No credentials found, redirecting...");
    window.location = "/login";
    return [];
  }
  const response = await fetch(
    `/api/quizes/${quizId}/questions/${questionId}/`,
    {
      method: 'DELETE',
      headers: {
        'Content-Type': 'Application/JSON',
        'Authorization': `Bearer ${token}`,
      },
    }
  );
  const text = await response.text();
  if (response.status === 401) {
    do_token_not_valid();
    return [];
  }
  if (response.status === 410) {
    console.log("success", JSON.parse(text));
    success(JSON.parse(text));
  } else {
    console.log("failed", text);
    fail(JSON.parse(text));
  }
};

const delete_answers_from_question_api = async (token, quizId, questionId, fail) => {
  const response = await fetch(
    `/api/quizes/${quizId}/questions/${questionId}/answers/`,
    {
      method: 'DELETE',
      headers: {
        'Content-Type': 'Application/JSON',
        'Authorization': `Bearer ${token}`,
      },
    }
  );
  const text = await response.text();
  if (response.status === 401) {
    do_token_not_valid();
    return false;
  }
  if (response.status === 410) {
    return true;
  } else {
    console.log("failed", text);
    fail(JSON.parse(text));
    return false;
  }
}

const put_question_api = async (quizId, question_data, success, fail) => {
  const token = await localStorage.getItem("userToken");
  if (token === null) {
    console.log("No credentials found, redirecting...");
    window.location = "/login";
    return [];
  }
  const deleted_answers = await delete_answers_from_question_api(token, quizId, question_data["question_id"], fail);
  if (!deleted_answers) {
    return;
  }
  const questionId = question_data["question_id"];
  const response = await fetch(
    `/api/quizes/${quizId}/questions/${questionId}/`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'Application/JSON',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(question_data)
    }
  );
  const text = await response.text();
  if (response.status === 401) {
    do_token_not_valid();
    return [];
  }
  if (response.status === 200) {
    console.log("success", JSON.parse(text));
    success(JSON.parse(text));
  } else {
    console.log("failed", text);
    fail(JSON.parse(text));
  }
};


const put_quiz_api = async (quizId, data, success, fail) => {
  const token = await localStorage.getItem("userToken");
  if (token === null) {
    console.log("No credentials found, redirecting...");
    window.location = "/login";
    return [];
  }
  const response = await fetch(
    `/api/quizes/${quizId}/`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'Application/JSON',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data)
    }
  );
  const text = await response.text();
  if (response.status === 401) {
    do_token_not_valid();
    return [];
  }
  if (response.status === 200) {
    console.log("success", JSON.parse(text));
    success(JSON.parse(text));
  } else {
    console.log("failed", text);
    fail(JSON.parse(text));
  }
};

const delete_quiz_api = async (quizId, success) => {
  const token = await localStorage.getItem("userToken");
  if (token === null) {
    console.log("No credentials found, redirecting...");
    window.location = "/login";
    return [];
  }
  const response = await fetch(
    `/api/quizes/${quizId}/`,
    {
      method: 'DELETE',
      headers: {
        'Content-Type': 'Application/JSON',
        'Authorization': `Bearer ${token}`,
      }
    }
  );
  const text = await response.text();
  if (response.status === 401) {
    do_token_not_valid();
    return [];
  }
  if (response.status === 410) {
    console.log("success", JSON.parse(text));
    success(JSON.parse(text));
  } else {
    console.log("failed", text);
    Object.entries(JSON.parse(text)).forEach(([key, value]) => {
      fail(`${key}: ${value}`);
    });
  }
};

const get_quiz_api = async (quizId, success, fail) => {
  const token = await localStorage.getItem("userToken");
  if (token === null) {
    console.log("No credentials found, redirecting...");
    window.location = "/login";
    return [];
  }
  const response = await fetch(
    `/api/quizes/${quizId}`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'Application/JSON',
        'Authorization': `Bearer ${token}`,
      }
    }
  );
  const text = await response.text();
  if (response.status === 401) {
    do_token_not_valid();
    return [];
  }
  if (response.status === 200) {
    var responseObj = JSON.parse(text);
    console.log("success", responseObj);
    success(responseObj);
  } else {
    console.log("failed", text);
    Object.entries(JSON.parse(text)).forEach(([key, value]) => {
      fail(`${key}: ${value}`);
    });
  }
};

const get_quiz_to_play_api = async (quizAlphanumericCode, success, fail) => {
  const response = await fetch(
    `/api/play/${quizAlphanumericCode}/`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'Application/JSON',
      }
    }
  );
  const text = await response.text();
  if (response.status === 200) {
    console.log("success", JSON.parse(text));
    success(JSON.parse(text));
  } else {
    console.log("failed", text);
    Object.entries(JSON.parse(text)).forEach(([key, value]) => {
      fail(`${key}: ${value}`);
    });
  }
};

const get_quiz_preview_api = async (quizAlphanumericCode, success, fail) => {
  const token = await localStorage.getItem("userToken");
  if (token === null) {
    console.log("No credentials found, redirecting...");
    window.location = "/login";
    return [];
  }
  const response = await fetch(
    `/api/preview/${quizAlphanumericCode}/`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'Application/JSON',
        'Authorization': `Bearer ${token}`,
      }
    }
  );
  const text = await response.text();
  if (response.status === 200) {
    console.log("success", JSON.parse(text));
    success(JSON.parse(text));
  } else {
    console.log("failed", text);
    Object.entries(JSON.parse(text)).forEach(([key, value]) => {
      fail(`${key}: ${value}`);
    });
  }
};

const post_answer_quiz_api = async (quizAlphanumericCode, data, success, fail) => {
  const response = await fetch(
    `/api/play/${quizAlphanumericCode}/`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'Application/JSON',
      },
      body: JSON.stringify(data)
    }
  );
  const text = await response.text();
  if (response.status === 200) {
    console.log("success", JSON.parse(text));
    success(JSON.parse(text));
  } else {
    console.log("failed", text);
    fail(JSON.parse(text));
  }
};