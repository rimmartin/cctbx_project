#include <boost/python/module.hpp>
#include <boost/python/class.hpp>
#include <scitbx/boost_python/iterator_wrappers.h>
#include <cctbx/eltbx/covalent_radii.h>

namespace cctbx { namespace eltbx { namespace covalent_radii {
namespace boost_python {

namespace {

  struct table_wrappers
  {
    typedef table w_t;

    static void
    wrap()
    {
      using namespace boost::python;
      class_<w_t>("table", no_init)
        .def(init<std::string const&, optional<bool> >())
        .def("label", &w_t::label)
        .def("radius", &w_t::radius)
        .def("esd", &w_t::esd)
      ;
    }
  };

  void init_module()
  {
    table_wrappers::wrap();
    scitbx::boost_python::iterator_wrappers<
      table, table_iterator>::wrap("table_iterator");
  }

} // namespace <anonymous>
}}}} // namespace cctbx::eltbx::covalent_radii::boost_python

BOOST_PYTHON_MODULE(cctbx_eltbx_covalent_radii_ext)
{
  cctbx::eltbx::covalent_radii::boost_python::init_module();
}
