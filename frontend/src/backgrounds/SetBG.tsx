import React from "react";
import Aurora from "../reactbits/Aurora/Aurora";

function SetBG() {
    return (
        <div className="fixed inset-0 -z-100">
            <Aurora
                colorStops={["#140A50", "#3A1120", "#330C0C"]}
                blend={0.5}
                amplitude={1.0}
                speed={0.5}
            />
        </div>
    );
}

export default React.memo(SetBG);