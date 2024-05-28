import React from "react";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-javascript";
import "ace-builds/src-noconflict/theme-monokai";
import "ace-builds/src-noconflict/theme-dracula";
import "ace-builds/src-noconflict/mode-python";
import { IoMdClose } from "react-icons/io";
import { Loader } from "components/loader/Loader";

interface IProps {
  closeEditor: () => void;
  setCodeValue: (e) => void;
  codeValue: string;
  handleCodeUpdate: () => void;
  isLoading: boolean;
}

const EditCodeComponent = ({
  closeEditor,
  setCodeValue,
  codeValue,
  handleCodeUpdate,
  isLoading,
}: IProps) => {
  const lines = codeValue?.split("\n");

  return (
    <div className="relative flex flex-col justify-center items-center rounded-[20px] bg-[#191919] mt-5">
      <div className="text_editabel pt-5 w-full h-full">
        <AceEditor
          mode="python"
          theme="dracula"
          onChange={(newCode) => {
            setCodeValue(newCode);
          }}
          value={codeValue}
          name="code-editor"
          width="100%"
          maxLines={Infinity}
          minLines={lines?.length + 2}
          fontSize={14}
          editorProps={{ $blockScrolling: true }}
        />
      </div>
      <button
        className="px-4 py-2 rounded-[12px] bg-black text-white text-[10px]  flex justify-end align-center mt-4 mb-2"
        onClick={handleCodeUpdate}
        disabled={isLoading}
      >
        {isLoading ? <Loader heigth="h-3" width="w-5" /> : `Submit`}
      </button>

      <div
        className=" absolute right-2 top-2 cursor-pointer"
        onClick={closeEditor}
      >
        <IoMdClose color={"white"} size="1.2rem" />
      </div>
    </div>
  );
};

export default EditCodeComponent;
