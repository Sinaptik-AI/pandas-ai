import React from "react";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-javascript";
import "ace-builds/src-noconflict/theme-monokai";
import "ace-builds/src-noconflict/theme-dracula";
import "ace-builds/src-noconflict/mode-python";
import { IoMdClose } from "react-icons/io";
import { Loader } from "components/loader/Loader";
import { Button } from "../ui/button";

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
      <Button
        type="button"
        onClick={handleCodeUpdate}
        disabled={isLoading}
        className="mt-4 mb-2"
      >
        {isLoading ? <Loader height="h-6" width="w-10" /> : `Submit`}
      </Button>

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
