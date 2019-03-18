//
// A C++ client designed to provide a simpler limited API
//
// This class leverages the wsWebsocketConnection class to provide simple
// acess to a few high level operaitons. All methods in the class return
// true on success and false on failure. When an error occurs the
// GetErrorText method can be used to obtain the text of the error.
//

#include <string>
#include <vector>

class wsWebsocketConnection;

class wsSimpleClient
{
public:
  wsSimpleClient();
  ~wsSimpleClient();

  // call before using this class, will attempt to connect
  // to the server. Returns true if succesfull
  bool Initialize(std::string const &host,
    std::string const &port,
    std::string const &target);

  // list the files available to load
  bool ListFileNames(std::vector<std::string> &result);

  // Load a dataset given a file name.
  // Returns true if successfull, false otherwise
  // Arguments include
  //   dsname - the name of the file to load
  //   ref - a reference for this dataset
  bool LoadDataSet(
    const std::string &dsname,
    int &ref
    );

  // Delete a dataset if possible. If the dataset is being
  // used as the input to another dataset it will not be
  // deleted.
  bool DeleteDataSet(int ref);

  // return json string about a dataset
  bool GetDataSetInformation(int ref,
    std::string &result
    );

  // Color a dataset by a  point field
  bool ColorDataSetByField(
    int input,
    std::string const &field,
    bool useCellData, // only false is supported right now
    int component // -1 means magnitude
    );

  // control the visibility of a dataset
  bool SetVisibility(int ref, bool val);

  // compute the isosorface of a dataset and return it as a
  // new dataset stored in result
  bool IsoSurface(
    int input,
    std::string const &field,
    std::vector<double> values,
    int &result
    );

  // compute the threshold of a dataset and return it as a
  // new dataset stored in result
  bool Threshold(
    int input,
    std::string const &field,
    bool fieldAssociationPoints, // true for points, false for cells
    double min,
    double max,
    bool allScalars,
    int &result
    );

  // compute streamlines for a dataset and return it as a
  // new dataset stored in result. The input dataset must
  // have a vector field to compute streamlines. The start
  // and end points define a line with numberOfSeeds seed
  // points on it.
  bool StreamTracer(
    int input,
    std::string const &field,
    double const startPoint[3],
    double const endPoint[3],
    int numberOfSeeds,
    int &result
    );

  // return the renderable data as a single json string
  // in gltf 2.0 format
  bool GetDataAsGLTF(
    std::string &result
    );

  // turn on debugging output, must be called after Initialize
  bool EnableDebugging();

  // if a command failed, get the error text
  std::string GetErrorText() { return this->ErrorText; }

  // generic helper signature
  bool CreateProxy(const char *name, int input, int &newID);

  // low level API to format and send your own messages
  // See https://github.com/Kitware/wslink for details
  // on the message format
  bool Send(
    std::string const &method,
    std::string const &arguments,
    std::string const &kwarguments,
    std::string &response
    );

protected:
  wsWebsocketConnection *Connection;
  std::string ErrorText;
};
