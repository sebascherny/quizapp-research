'use strict';

class ModalDiv extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return <div style={{ background: "#00000060" }}
            className={"modal " + (this.props.showModal ? " show d-block" : " d-none")} tabIndex="-1" role="dialog">
            <div className="modal-dialog shadow">
                <form method="post">
                    <div className="modal-content">
                        <div className="modal-header">
                            <h5 className="modal-title">{this.props.modalDescription}</h5>
                            <button type="button" className="btn-close" onClick={() => { this.props.setShowModal(false) }} aria-label="Close"></button>
                        </div>
                        <div className="modal-body">
                            <label>Title</label>
                            <div className="form-group">
                                <input type="text" className="form-control" name="title" id="titleInput"
                                    value={this.props.title} onChange={(e) => { this.props.setTitle(e.target.value) }}
                                    placeholder="Title" />
                            </div>
                            <small className="form-text text-muted">{this.props.error}</small>
                        </div>
                        <div className="modal-footer">
                            <button type="button" className="btn btn-secondary" onClick={() => { this.props.setShowModal(false) }} data-bs-dismiss="modal">Close</button>
                            <button type="submit" className="btn btn-primary" onClick={this.props.onclickFnc}>{this.props.btnText}</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    }
}