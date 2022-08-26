'use strict';
const e = React.createElement;


function App() {
  const [title, setTitle] = React.useState("");
  const [isPublished, setIsPublished] = React.useState(false);
  const [questions, setQuestions] = React.useState([]);
  const [alphanumericCode, setAlphanumericCode] = React.useState("");
  const [showModal, setShowModal] = React.useState(false);
  const [selectedQuestionIdx, setSelectedQuestionIdx] = React.useState(null);
  const [error, setError] = React.useState("");
  const [question, setQuestion] = React.useState("");
  const [numberOfAnswers, setNumberOfAnswers] = React.useState(0);
  const [nextIndex, setNextIndex] = React.useState(0);
  const [loggedInUsername, setLoggedInUsername] = React.useState(null);
  const [newTitle, setNewTitle] = React.useState("");
  const [modalError, setModalError] = React.useState("");

  const copyLinkToClipboard = () => {
    const link = getPublishedLink();
    navigator.clipboard.writeText(link);
    copyLinkButton.innerHTML = "Copied!";
    setTimeout(() => { copyLinkButton.innerHTML = "Copy link" }, 500);
  };

  const removeAnswer = (answerNum) => {
    document.querySelector("#div_answers_" + answerNum).remove();
    setNumberOfAnswers(numberOfAnswers => numberOfAnswers - 1);
  }

  const addAnswer = (currentNextIndexParam, focusText) => {
    var currentNextIndex = currentNextIndexParam;
    if (currentNextIndex === null) {
      currentNextIndex = nextIndex;
    }
    setNumberOfAnswers(numberOfAnswers => numberOfAnswers + 1);
    const onClickRemoveButton = () => removeAnswer(currentNextIndex);
    const txtAnswer = document.createElement("input");
    txtAnswer.setAttribute("placeholder", "Answer");
    txtAnswer.setAttribute("id", "txt_answer_" + currentNextIndex);
    txtAnswer.setAttribute("style", "width: 80%;");
    if (isPublished) {
      txtAnswer.setAttribute("disabled", "disabled");
    }
    const switchDiv = document.createElement("div");
    switchDiv.classList.add("form-check");
    switchDiv.classList.add("form-switch");
    switchDiv.setAttribute("style", "align-self: center; margin-left: 2%; margin-right: 5%;");
    const switchInput = document.createElement("input");
    switchInput.classList.add("form-check-input");
    switchInput.setAttribute("role", "switch");
    switchInput.setAttribute("type", "checkbox");
    switchInput.checked = false;
    switchInput.setAttribute("id", "switch_is_correct_answer_" + currentNextIndex);
    if (isPublished) {
      switchInput.setAttribute("disabled", "disabled");
    }
    const switchLabel = document.createElement("label");
    switchLabel.innerHTML = "Correct";
    switchLabel.classList.add("form-check-label");
    switchDiv.append(switchInput);
    switchDiv.append(switchLabel);
    const removeButton = document.createElement("button");
    removeButton.setAttribute("id", "remove_answer_" + currentNextIndex);
    if (isPublished) {
      removeButton.setAttribute("disabled", "disabled");
    }
    removeButton.onclick = function () {
      removeAnswer(currentNextIndex);
      return false;
    }
    removeButton.innerHTML = "Remove";
    removeButton.classList.add("btn");
    removeButton.classList.add("shadow");
    const newAnswerDiv = document.createElement("div")
    newAnswerDiv.setAttribute("id", "div_answers_" + currentNextIndex);
    newAnswerDiv.append(txtAnswer);
    newAnswerDiv.append(switchDiv);
    newAnswerDiv.append(removeButton);
    newAnswerDiv.setAttribute("style", "margin-bottom: 10px; display: flex;");
    document.querySelector("#all_answers").append(newAnswerDiv);
    if (focusText) {
      txtAnswer.focus();
    }
  };

  const loadQuestion = (idx) => {
    if (idx >= questions.length) {
      return;
    }
    loadQuestionFromQuestion(questions[idx], idx);
  };

  const loadQuestionFromQuestion = (qq, idx) => {
    setNumberOfAnswers(0);
    setQuestion(qq.question);
    document.getElementById("question_type").value = qq.is_multiple_answers ? "multiple" : "single";
    setSelectedQuestionIdx(idx);
    document.getElementById("all_answers").innerHTML = "";
    var currentNextIndex = nextIndex;
    qq.answers.map((ans, ans_idx) => {
      addAnswer(currentNextIndex, false);
      document.getElementById("txt_answer_" + currentNextIndex).value = ans.answer;
      document.getElementById("switch_is_correct_answer_" + currentNextIndex).checked = ans.correct;
      currentNextIndex += 1;
    });
    setNextIndex(currentNextIndex);
    setError("");
    for (const x of document.querySelectorAll('[id^="selectQuestionBtn"]')) {
      x.classList.remove("active");
    }
    document.getElementById("selectQuestionBtn" + idx).classList.add("active");
    const questionInput = document.getElementById("questionInput");
    questionInput.focus();
  };

  const quizId = getQuizId();

  const blockAnswersSitchAndRemoveButton = () => {
    setDisabledPropertyToAnswers(true);
  };

  const unblockAnswersSitchAndRemoveButton = () => {
    setDisabledPropertyToAnswers(false);
  };

  const setDisabledPropertyToAnswers = (disableBool) => {
    for (const elem of document.querySelectorAll('[id^="switch_is_correct_answer_"]')) {
      if (disableBool) {
        elem.setAttribute("disabled", "disabled");
      } else {
        elem.removeAttribute("disabled");
      }
    }
    for (const elem of document.querySelectorAll('[id^="remove_answer_"]')) {
      if (disableBool) {
        elem.setAttribute("disabled", "disabled");
      } else {
        elem.removeAttribute("disabled");
      }
    }
    for (const elem of document.querySelectorAll('[id^="txt_answer_"]')) {
      if (disableBool) {
        elem.setAttribute("disabled", "disabled");
      } else {
        elem.removeAttribute("disabled");
      }
    }
  };

  const success = (data, loadIndex = 0) => {
    setQuestions(data.data.questions);
    setTitle(data.data.title);
    setIsPublished(data.data.is_published);
    setAlphanumericCode(data.data.alphanumeric_code)
    if (data.data.questions.length > 0) {
      if (loadIndex === null || loadIndex >= data.data.questions.length) {
        loadQuestionFromQuestion(data.data.questions[data.data.questions.length - 1], data.data.questions.length - 1);
      } else {
        loadQuestionFromQuestion(data.data.questions[loadIndex], loadIndex);
      }
      if (data.data.is_published) {
        blockAnswersSitchAndRemoveButton();
      } else {
        unblockAnswersSitchAndRemoveButton();
      }
    }
  };

  const getData = (loadIndex) => {
    get_quiz_api(quizId, (data) => success(data, loadIndex), (text) => { console.log("Error: ", text) });
    getLoggedInUsername((username) => { setLoggedInUsername(username) });
  };
  React.useEffect(() => {
    getData(0);
  }, []);

  const getCurrentQuestionObject = () => {
    const answers_divs = document.querySelectorAll('[id^="div_answers_"]');
    var answers_list = [];
    for (var i = 0; i < answers_divs.length; i++) {
      const ansDiv = answers_divs[i];
      const num = ansDiv.id.substring("div_answers_".length);
      const answer = document.getElementById("txt_answer_" + num).value;
      const correct = document.getElementById("switch_is_correct_answer_" + num).checked;
      answers_list.push({ correct, answer });
    }
    const questionText = document.getElementById("questionInput").value;
    const is_multiple_answers = document.getElementById("question_type").value === "multiple";
    return { "question": questionText, "answers": answers_list, is_multiple_answers };
  }

  const getCorrectAnswers = (qObject) => {
    var correctAnswers = 0;
    for (const ans of qObject.answers) {
      if (ans.correct) {
        correctAnswers += 1;
      }
    }
    return correctAnswers;
  };

  const saveQuestion = (e) => {
    e.preventDefault();
    saveQuestionFromCode(selectedQuestionIdx);
  };

  const saveQuestionFromCode = (loadIndex = null) => {
    setError("");
    const currentQuestionObject = getCurrentQuestionObject();
    if (selectedQuestionIdx === null) {
      var questionsPlusNew = questions;
      questionsPlusNew.push(currentQuestionObject);
      put_quiz_api(quizId, { "questions": questionsPlusNew }, () => { getData(loadIndex) }, (errors) => {
        console.log(errors);
      });
    } else {
      var questionsWithEdition = questions;
      questionsWithEdition[selectedQuestionIdx] = currentQuestionObject;
      put_quiz_api(quizId, { "questions": questionsWithEdition }, () => { getData(loadIndex) }, (errors) => {
        console.log(errors);
      });
    }
  };

  const deleteQuestion = () => {
    /*Swal.fire({
      title: 'Are you sure you want to delete the question?',
      text: "This action cannot be reverted",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, delete'
    }).then((result) => {
      if (result.isConfirmed) {*/
    var questionsWithoutDeleted = [];
    for (var i = 0; i < questions.length; i++) {
      if (i != selectedQuestionIdx) {
        questionsWithoutDeleted.push(questions[i]);
      }
    }
    put_quiz_api(quizId, { "questions": questionsWithoutDeleted }, () => {
      Swal.fire({
        title: 'Question deleted',
        text: "",
        icon: 'success',
        timer: 500,
      });
      getData(selectedQuestionIdx);
      for (const x of document.querySelectorAll('[id^="selectQuestionBtn"]')) {
        const idxNum = parseInt(x.id.substring("selectQuestionBtn".length));
        if (idxNum >= selectedQuestionIdx && idxNum < questions.length) {
          const nextBtn = document.getElementById("selectQuestionBtn" + (idxNum + 1));
          if (nextBtn !== null) {
            if (nextBtn.classList.contains("btn-warning")) {
              x.classList.add("btn-warning");
            } else {
              x.classList.remove("btn-warning");
            }
          }
        }
      }
    }, (errors) => {
      console.log(errors);
    });
    //}
    //});
  };

  const newQuestion = () => {
    saveQuestionFromCode(null);
    var questionsPlusNew = questions;
    questionsPlusNew.push({ "question": "", "is_multiple_answers": false, "answers": [] });
    put_quiz_api(quizId, { "questions": questionsPlusNew }, () => { getData(null) }, (errors) => {
      console.log(errors);
    });
  };

  const changePublishStatus = () => {
    if (!isPublished) {
      if (selectedQuestionIdx !== null) {
        saveQuestionFromCode(selectedQuestionIdx);
      } else {
        setSelectedQuestionIdx(0);
        saveQuestionFromCode(0);
      }
    }
    setTimeout(() => {
      for (const x of document.querySelectorAll('[id^="selectQuestionBtn"]')) {
        x.classList.remove("btn-warning");
      }
      put_quiz_api(quizId, { "is_published": !isPublished }, () => {
        Swal.fire({
          title: isPublished ? 'Quiz unpublished!' : 'Quiz published!',
          text: "",
          icon: 'success',
          timer: 500,
        });
        getData(selectedQuestionIdx);
      }, (errorsData) => {
        const errors = errorsData.errors;
        for (const errorMap of errors) {
          if (errorMap["questions"]) {
            setError("Check yellow questions before publishing")
            for (const [key, value] of Object.entries(errorMap["questions"])) {
              document.getElementById("selectQuestionBtn" + key).classList.add("btn-warning");
            }
          } else if (errorMap["length"]) {
            setError(errorMap["length"]);
          }
        }
      });
    }, 100);
  };

  const getPublishedLink = () => {
    return window.location.origin + "/play/" + alphanumericCode;
  }

  if (!title) {
    return (
      <div>
        <AppHeader loggedInUsername={loggedInUsername} setLoggedInUsername={setLoggedInUsername} redirectWhenLoggedOut={true} />
        <div style={{
          maxWidth: "800px", margin: "auto", marginTop: "1em", marginBottom: "1em",
          padding: "1em"
        }} className="shadow">
          <div><h6>Quiz not found</h6></div>
        </div>
      </div>
    )
  }

  const editTitle = () => {
    setNewTitle(title);
    setModalError("");
    setShowModal(true);
    const titleInput = document.getElementById("titleInput");
    setTimeout(() => { titleInput && titleInput.focus() }, 1);
  };

  const saveTitle = (e) => {
    e.preventDefault();
    setModalError("");
    if (newTitle.length === 0) {
      setModalError("Title is required");
      return;
    }
    put_quiz_api(quizId, { title: newTitle }, () => { getData(selectedQuestionIdx); });
    setShowModal(false);
  };


  return (
    <div>
      <ModalDiv showModal={showModal} setShowModal={setShowModal}
        modalDescription="Set title" title={newTitle} setTitle={setNewTitle}
        error={modalError} btnText="Save" onclickFnc={saveTitle} />
      <AppHeader loggedInUsername={loggedInUsername} setLoggedInUsername={setLoggedInUsername} redirectWhenLoggedOut={true} />
      <div style={{
        maxWidth: "800px", margin: "auto", marginTop: "1em", marginBottom: "1em",
        padding: "1em"
      }} className="shadow">
        <h3 style={{ textAlignLast: "center" }}>{title}</h3>
        <div className="form-check form-switch">
          <input className="form-check-input" type="checkbox" role="switch" id="publishedSwitch" checked={isPublished} onChange={() => { changePublishStatus() }} />
          <label className="form-check-label" htmlFor="publishedSwitch">Published</label>
          <button className="btn btn-default rounded-pill float-end" style={{ marginLeft: "auto" }}
            onClick={(e) => { editTitle() }} disabled={isPublished}>Change title</button>
        </div>
        <small className="form-text text-muted">{error}</small>
        {isPublished &&
          <div style={{ flexDirection: "row", marginBottom: "5px", marginTop: "10px" }}>
            <label>Link:</label>
            <a style={{ marginLeft: "10px", marginRight: "10px" }} href={"/play/" + alphanumericCode}>{getPublishedLink()}</a>
            <a id="copyLinkButton" className="btn btn-info" style={{ marginLeft: "auto" }} onClick={() => { copyLinkToClipboard() }}>Copy link</a>
          </div>}
      </div>
      <div style={{
        maxWidth: "800px", margin: "auto", marginTop: "1em", marginBottom: "1em",
        padding: "1em"
      }} className="shadow">
        <div className="btn-group" id="questions_buttons" style={{ display: "flex", flexDirection: "row", marginBottom: "5px" }}>
          {
            questions.length === 0 &&
            <a id={"selectQuestionBtn0"} className="btn btn-primary" style={{ maxWidth: "40px" }}
              onClick={() => { saveQuestionFromCode(0); loadQuestion(0) }}
            >1</a>
          }
          {
            questions.map((row, idx) =>
              <a id={"selectQuestionBtn" + idx} key={idx} className="btn btn-primary" style={{ maxWidth: "40px" }}
                onClick={() => { if (!isPublished) { saveQuestionFromCode(idx); } loadQuestion(idx) }}
              >{idx + 1}</a>
            )
          }
          <button className="btn btn-light" style={{ marginLeft: "auto", maxWidth: "150px" }}
            onClick={newQuestion} disabled={questions.length >= 10 || isPublished}
          >New question</button>
        </div>


        <div>
          <div style={{ marginBottom: "30px", marginTop: "30px" }}>
            <button className="btn btn-danger" style={{ marginLeft: "auto" }}
              onClick={(e) => { deleteQuestion() }} disabled={questions.length <= 1 || isPublished}>X</button>
            <input style={{ marginLeft: "5%", marginRight: "10%", width: "60%" }} id="questionInput" placeholder="Question"
              value={question} onChange={(e) => { setQuestion(e.target.value) }} disabled={isPublished}></input>
            <select id="question_type" defaultValue={"single"} disabled={isPublished}>
              <option value="single" > Single answer</option>
              <option value="multiple" > Multiple answers</option>
            </select>
          </div>
          <div style={{ display: "flex", flexDirection: "column", marginBottom: "5px" }} id="all_answers">
          </div>
          <button className="btn btn-info" style={{ marginLeft: "auto" }}
            onClick={(e) => { addAnswer(null, true); setNextIndex(nextIndex + 1); }} disabled={numberOfAnswers >= 5 || isPublished}>Add answer</button>
        </div>

      </div>
    </div>
  );
}

const domContainer = document.querySelector('#reactAppContainer');
ReactDOM.render(
  e(App),
  domContainer
);
