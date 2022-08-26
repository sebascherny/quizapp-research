'use strict';
const e = React.createElement;


function App() {
  const [list, setList] = React.useState([]);
  const [pages, setPages] = React.useState([]);
  const [page, setPage] = React.useState(0);
  const [showModal, setShowModal] = React.useState(false);
  const [modalDescription, setModalDescription] = React.useState("");
  const [itemId, setItemId] = React.useState(null);
  const [creatingNewQuiz, setCreatingNewQuiz] = React.useState(null);
  const [error, setError] = React.useState("");
  const [title, setTitle] = React.useState("");
  const [loggedInUsername, setLoggedInUsername] = React.useState(null);


  function keyListener(event) {
    event = event || window.event;
    var key = event.which || event.key || event.keyCode;
    if (key === 27) { // escape
      setShowModal(false);
    }
  }

  window.addEventListener('keyup', keyListener, false);

  const success = (data) => {
    setList(data.data);
    const newPages = [];
    if (data.count > 10) {
      for (let i = 0; i < Math.ceil(data.count / 10); i++) {
        newPages.push({
          name: (i + 1).toString(),
          page: i,
        });
      }
      if (page > newPages.length - 1) {
        setPage(page - 1);
      }
    } else {
      setPage(0);
    }
    setPages(newPages);
  };

  const getData = () => {
    get_quizes_api(page, success, (text) => { console.log("Error: ", text) });
    getLoggedInUsername((username) => { setLoggedInUsername(username) });
  };
  React.useEffect(() => {
    getData();
  }, [page]);

  const saveQuiz = (e) => {
    e.preventDefault();
    setError("");
    if (title.length === 0) {
      setError("Title is required");
      return;
    }
    if (itemId === null) {
      post_quiz_api({ title }, () => { getData(); });
    } else {
      put_quiz_api(itemId, { title }, () => { getData(); });
      window.location = window.location.origin + "/dashboard/" + itemId;
    }
    setShowModal(false);
  };

  const saveTitle = (e) => {
    e.preventDefault();
    setError("");
    if (title.length === 0) {
      setError("Title is required");
      return;
    }
    put_quiz_api(itemId, { title }, () => { getData(); });
    setShowModal(false);
  };

  const deleteQuiz = (quizId) => {
    Swal.fire({
      title: 'Are you sure you want to delete the quiz?',
      text: "This action cannot be reverted",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, delete'
    }).then((result) => {
      if (result.isConfirmed) {
        delete_quiz_api(quizId, () => {
          Swal.fire({
            title: 'Quiz deleted',
            text: "",
            icon: 'success',
            timer: 1000,
          });
          getData();
        }, (error) => console.log(error));
      }
    });
  };

  const newQuiz = () => {
    setModalDescription("New quiz");
    setItemId(null);
    setTitle("");
    setError("");
    setCreatingNewQuiz(true);
    setShowModal(true);
    const titleInput = document.getElementById("titleInput");
    setTimeout(() => { titleInput && titleInput.focus() }, 1);
  };

  const editTitle = (data) => {
    setModalDescription("Edit title");
    setItemId(data.id);
    setTitle(data.title);
    setError("");
    setCreatingNewQuiz(false);
    setShowModal(true);
    const titleInput = document.getElementById("titleInput");
    setTimeout(() => { titleInput && titleInput.focus() }, 1);
  };

  const getPublishedLink = (alphanumeric_code) => {
    return window.location.origin + "/play/" + alphanumeric_code;
  };

  const copyLinkToClipboard = (alphanumeric_code) => {
    const link = getPublishedLink(alphanumeric_code);
    navigator.clipboard.writeText(link);
    copyLinkButton.innerHTML = "Copied!";
    setTimeout(() => { copyLinkButton.innerHTML = "Copy link" }, 500);
  };

  return (
    <div>
      <ModalDiv showModal={showModal} setShowModal={setShowModal}
        modalDescription={modalDescription} title={title} setTitle={setTitle}
        error={error} btnText={creatingNewQuiz ? "Add questions" : "Save"}
        onclickFnc={creatingNewQuiz ? saveQuiz : saveTitle} />
      <AppHeader loggedInUsername={loggedInUsername} setLoggedInUsername={setLoggedInUsername} redirectWhenLoggedOut={true} />
      <div style={{
        maxWidth: "800px", margin: "auto", marginTop: "1em", marginBottom: "1em",
        padding: "1em"
      }} className="shadow">
        <div style={{ display: "flex", flexDirection: "row", marginBottom: "5px" }}>
          {pages.length > 0 && <nav className="d-lg-flex justify-content-lg-end dataTables_paginate paging_simple_numbers">
            <ul className="pagination">
              <li className={"page-item " + (page === 0 ? "disabled" : "")}
                onClick={(e) => {
                  e.preventDefault();
                  setPage(Math.max(page - 1, 0));
                }}>
                <a className="page-link" href="#" aria-label="Previous">
                  <span aria-hidden="true">«</span>
                </a>
              </li>
              {pages.map((el) => (
                <li key={"page" + el.page}
                  onClick={(e) => { setPage(el.page); }} className={"page-item " + (page === el.page ? "active" : "")}>
                  <a className="page-link" href="#">
                    {el.name}
                  </a></li>))}
              <li className={"page-item " + (page === pages.length - 1 ? "disabled" : "")} onClick={(e) => {
                setPage(Math.min(page + 1, pages.length - 1));
              }}><a className="page-link" href="#" aria-label="Next"><span
                aria-hidden="true">»</span></a></li>
            </ul>
          </nav>}
          <a className="btn btn-light" style={{ marginLeft: "auto" }}
            onClick={newQuiz}
          >New quiz</a>
        </div>
        {list.length > 0 &&
          <table className="table table-hover caption-top">
            <thead className="table-light">
              <tr>
                <th>Title</th>
                <th># questions</th>
              </tr>
            </thead>
            <tbody>
              {list.map((row) =>
                <tr key={row.id}>
                  <td>{row.title}</td>
                  <td>{row.questions.length}{" "}{row.is_published && ([
                    <a key="1" href={getPublishedLink(row.alphanumeric_code)}>(Play)</a>,
                    //<a key="2" id="copyLinkButton" className="btn btn-info" style={{ marginLeft: "auto" }} onClick={() => { copyLinkToClipboard(row.alphanumeric_code) }}>Copy link</a>
                  ])}</td>
                  <td>
                    <button className="btn btn-default rounded-pill" style={{ marginLeft: "auto" }}
                      onClick={(e) => { editTitle(row) }} disabled={row.is_published}>Change title</button>{" "}
                    <a className="btn btn-info rounded-pill" style={{ marginLeft: "auto" }}
                      href={window.location.origin + "/dashboard/" + row.id}>Edit questions</a>{" "}
                    <a className="btn btn-danger rounded-pill" style={{ marginLeft: "auto" }}
                      onClick={(e) => { deleteQuiz(row.id) }}>Remove</a>
                    <a className="btn btn-light rounded-pill" style={{ marginLeft: "auto" }}
                      href={window.location.origin + "/preview/" + row.alphanumeric_code} target="_blank">Preview</a>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        }
      </div>
    </div>
  );
}

const domContainer = document.querySelector('#reactAppContainer');
ReactDOM.render(
  e(App),
  domContainer
);
