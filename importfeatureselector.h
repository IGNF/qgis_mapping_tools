#ifndef IMPORTFEATURESELECTOR2_H
#define IMPORTFEATURESELECTOR2_H

#include <QDialog>

namespace Ui {
class importFeatureSelector2;
}

class importFeatureSelector2 : public QDialog
{
    Q_OBJECT

public:
    explicit importFeatureSelector2(QWidget *parent = 0);
    ~importFeatureSelector2();

private:
    Ui::importFeatureSelector2 *ui;
};

#endif // IMPORTFEATURESELECTOR2_H
