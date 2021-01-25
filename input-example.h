#ifndef B3F6FA37_57D3_45BF_A789_EB0E7FF55DCB
#define B3F6FA37_57D3_45BF_A789_EB0E7FF55DCB

#include <opencv2/opencv.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/video.hpp>

#include <string>

namespace BP {

static const std::string RECT = "RECT";
static const std::string CROSS = "CROSS";
static const std::string ELLIPSE = "ELLIPSE";
static const std::string KNN = "KNN";
static const std::string MOG2 = "MOG2";

struct Parameters {
    std::string bgSubtractor;
    bool bgSubVerbose;

    int blur;
    bool blurVerbose;

    std::string erosion;
    bool erosionVerbose;
    int erosionSize;

    std::string dilation;
    int dilationSize;
    bool dilationVerbose;

    int threshold;
    bool thresholdVerbose;
};



using namespace cv;

class BasicProcessing{
public:
    static BasicProcessing& getInstance();
    virtual ~BasicProcessing();
    void initialize(Parameters& m_params);
    void process(Mat& frame);
    const Mat& getResult();

private:
    void blur(Mat& frame);
    void dilation(Mat& frame);
    void erosion(Mat& frame);
    void binarize(Mat& frame);

    BasicProcessing();
    Parameters m_params;
    Ptr<BackgroundSubtractor> m_bgSubtractor;
    Mat m_result;
};


}
#endif /* B3F6FA37_57D3_45BF_A789_EB0E7FF55DCB */
