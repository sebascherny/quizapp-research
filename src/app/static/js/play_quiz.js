'use strict';
const e = React.createElement;


function App() {
  const [title, setTitle] = React.useState("");
  const [questions, setQuestions] = React.useState([]);
  const [loggedInUsername, setLoggedInUsername] = React.useState(null);
  const [correctAnswers, setCorrectAnswers] = React.useState(null);

  const quizAlphanumericCode = getQuizAlphanumericCode();
  const isPreview = getIsPreview();
  document.title = isPreview ? "Preview quiz" : "Play quiz";

  const success = (data, loadIndex = 0) => {
    setQuestions(data.data.questions);
    setTitle(data.data.title);
  };

  const getData = () => {
    if (isPreview) {
      get_quiz_preview_api(quizAlphanumericCode, success, (error) => { console.log("Error: ", error) });
    } else {
      get_quiz_to_play_api(quizAlphanumericCode, success, (error) => { console.log("Error: ", error) });
    }
    getLoggedInUsername((username) => { setLoggedInUsername(username) });
  };
  React.useEffect(() => {
    getData();
  }, []);

  const submitAnswers = () => {
    var answers = [];
    for (const questionDiv of document.querySelectorAll('[id^="div_question_"]')) {
      const questionNum = questionDiv.id.substring("div_question_".length);
      const inputIdPrefix = 'question_' + questionNum + '_answer_';
      var ans_i = []
      for (const answerInput of questionDiv.querySelectorAll('[id^="' + inputIdPrefix + '"]')) {
        const answerIdx = answerInput.id.substring(inputIdPrefix.length);
        if (answerInput.checked) {
          ans_i.push(parseInt(answerIdx));
        }
      }
      answers.push(ans_i);
    }
    post_answer_quiz_api(quizAlphanumericCode, { answers },
      (result) => {
        setCorrectAnswers(result["data"]["correct"]);
      },
      (error) => { console.log(error) });
  };

  const playAgain = () => {
    setCorrectAnswers(null);
  }

  return (
    <div>
      <AppHeader loggedInUsername={loggedInUsername} setLoggedInUsername={setLoggedInUsername} redirectWhenLoggedOut={isPreview} />
      <div style={{
        maxWidth: "800px", margin: "auto", marginTop: "1em", marginBottom: "1em",
        padding: "1em"
      }} className="shadow">
        {!title && <div><h6>Quiz not found</h6></div>}
        {title &&
          <div style={{ textAlignLast: "center", flexDirection: "row" }}>
            <h3>{title}{isPreview ? " (Preview)" : ""}</h3>
          </div>
        }
      </div>
      {title && correctAnswers === null &&
        <div style={{
          maxWidth: "800px", margin: "auto", marginTop: "1em", marginBottom: "1em",
          padding: "1em"
        }} className="shadow">
          <div>
            {questions.map((row, questionIdx) =>
              <div id={"div_question_" + questionIdx} key={questionIdx}>
                <div>
                  <h4 style={{ marginBottom: "15px", marginTop: "30px" }} >Question {questionIdx + 1}</h4>
                  <label>{row.question}</label>
                </div>
                {row.is_multiple_answers && row.answers.map((answer, answerIdx) =>
                  <div style={{ marginTop: "20px" }} key={answerIdx} className="form-check">
                    <input className="form-check-input" type="checkbox" value="APCLAPA"
                      id={"question_" + questionIdx + "_answer_" + answerIdx} />
                    <label className="form-check-label" htmlFor={"question_" + questionIdx + "_answer_" + answerIdx}>
                      {answer.answer}
                    </label>
                  </div>
                )}
                {!row.is_multiple_answers && row.answers.map((answer, answerIdx) =>
                  <div style={{ marginTop: "20px" }} key={answerIdx} className="form-check">
                    <input className="form-check-input" type="radio" name={"question_" + questionIdx}
                      id={"question_" + questionIdx + "_answer_" + answerIdx} />
                    <label className="form-check-label" htmlFor={"question_" + questionIdx}>
                      {answer.answer}
                    </label>
                  </div>)}
              </div>)}
          </div>
        </div>
      }
      {title && correctAnswers !== null &&
        [<div key="submission_message_div" style={{
          display: "flex", flexDirection: "row",
          maxWidth: "800px", margin: "auto", marginTop: "1em", marginBottom: "1em",
          padding: "1em"
        }} className="shadow">
          <div>
            {correctAnswers * 2 >= questions.length ? "Congratulations! " : ""}You answered {correctAnswers}/{questions.length} correctly.
          </div>
        </div>,
        <div key="play_again_div">
          <button style={{
            display: "flex", flexDirection: "row", margin: "auto"
          }} className="btn btn-submit shadow" onClick={() => { playAgain(); }}>Play again</button>
        </div>]
      }
      {title && correctAnswers === null && !isPreview &&
        <button style={{
          display: "flex", flexDirection: "row", margin: "auto"
        }} className="btn btn-submit shadow" onClick={() => { submitAnswers(); }}>Submit answers</button>

      }
    </div>
  );
}

const domContainer = document.querySelector('#reactAppContainer');
ReactDOM.render(
  e(App),
  domContainer
);
